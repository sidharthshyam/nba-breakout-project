"""Analyze whether NBA breakout seasons are sustained."""

import numpy as np
import pandas as pd

import ba
import seaborn as sns
import matplotlib.pyplot as plt


def add_following_season(
    breakouts: pd.DataFrame,
    stats: pd.DataFrame,
    performance_metrics: list[str],
) -> pd.DataFrame:
    """Attach each player's following-season statistics to breakout rows."""
    follow_up_cols = [
        "PLAYER_ID",
        "SEASON_START",
        "SEASON",
        "TOTAL_MIN",
        "MPG",
        "USG_PCT",
    ] + performance_metrics

    follow_up = stats[follow_up_cols].copy()

    # Match each follow-up season to the breakout season before it.
    follow_up["SEASON_START"] = follow_up["SEASON_START"] - 1

    rename = {
        "SEASON": "FOLLOW_UP_SEASON",
        "TOTAL_MIN": "FOLLOW_UP_TOTAL_MIN",
        "MPG": "FOLLOW_UP_MPG",
        "USG_PCT": "FOLLOW_UP_USG_PCT",
    }

    for metric in performance_metrics:
        rename[metric] = f"FOLLOW_UP_{metric}"

    follow_up = follow_up.rename(columns=rename)

    return breakouts.merge(
        follow_up,
        on=["PLAYER_ID", "SEASON_START"],
        how="left",
        validate="one_to_one",
    )


def filter_eligible_follow_ups(
    breakouts: pd.DataFrame,
    minute_cutoff: int,
) -> pd.DataFrame:
    """Keep breakouts with an available and eligible following season."""
    eligible = (
        breakouts["FOLLOW_UP_SEASON"].notna()
        & (breakouts["FOLLOW_UP_TOTAL_MIN"] >= minute_cutoff)
    )

    return breakouts[eligible].copy()


def calculate_retention(
    breakouts: pd.DataFrame,
    performance_metrics: list[str],
) -> pd.DataFrame:
    """Calculate improvement retention for each qualifying metric."""
    breakouts = breakouts.copy()

    for metric in performance_metrics:
        qualified = breakouts[f"QUALIFIED_{metric}"]

        for index, value in qualified.items():
            if value:
                previous = breakouts.at[index, f"PREV_{metric}"]
                current = breakouts.at[index, metric]
                follow_up = breakouts.at[
                    index,
                    f"FOLLOW_UP_{metric}",
                ]

                retention = (
                    (follow_up - previous)
                    / (current - previous)
                )
            else:
                retention = np.nan

            breakouts.at[
                index,
                f"RETENTION_{metric}",
            ] = retention

    return breakouts


def classify_sustainability(
    breakouts: pd.DataFrame,
    retention_cols: list[str],
) -> pd.DataFrame:
    """Calculate average retention and classify each breakout."""
    breakouts = breakouts.copy()

    breakouts["AVERAGE_RETENTION"] = (
        breakouts[retention_cols].mean(axis=1)
    )

    breakouts["SUSTAINED_OR_IMPROVED"] = (
        breakouts["AVERAGE_RETENTION"] >= 0.8
    )

    results = []

    for retention in breakouts["AVERAGE_RETENTION"]:
        if retention > 1:
            results.append("Improved further")
        elif retention >= 0.8:
            results.append("Sustained at least 80%")
        else:
            results.append("Regressed")

    breakouts["SUSTAINABILITY_RESULT"] = results

    return breakouts


def create_summary(breakouts: pd.DataFrame) -> pd.DataFrame:
    """Create a table of sustainability counts and percentages."""
    summary = (
        breakouts["SUSTAINABILITY_RESULT"]
        .value_counts()
        .reset_index()
    )

    summary.columns = ["RESULT", "COUNT"]

    summary["PERCENT"] = (
        summary["COUNT"] / summary["COUNT"].sum() * 100
    )

    return summary


def print_results(
    breakouts: pd.DataFrame,
    summary: pd.DataFrame,
    retention_cols: list[str],
) -> None:
    """Print sustainability results and example breakout rows."""
    print("\nSustainability outcomes:")
    print(summary.round(2).to_string(index=False))

    print("\nAverage retention summary:")
    print(
        breakouts["AVERAGE_RETENTION"]
        .describe()
        .round(3)
    )

    print("\nRetention by performance dimension:")
    print(
        breakouts[retention_cols]
        .describe()
        .round(3)
    )

    display_cols = [
        "PLAYER_NAME",
        "SEASON",
        "FOLLOW_UP_SEASON",
        "AVERAGE_RETENTION",
        "SUSTAINABILITY_RESULT",
    ] + retention_cols

    print("\nFirst 20 sustainability results:")
    print(
        breakouts[display_cols]
        .head(20)
        .round(3)
        .to_string(index=False)
    )

    season_stat_cols = [
        "PLAYER_NAME",
        "SEASON",
        "FOLLOW_UP_SEASON",
        "PTS_PER_36",
        "FOLLOW_UP_PTS_PER_36",
        "TS_PCT",
        "FOLLOW_UP_TS_PCT",
        "AST_PCT",
        "FOLLOW_UP_AST_PCT",
        "REB_PCT",
        "FOLLOW_UP_REB_PCT",
        "TOTAL_MIN",
        "FOLLOW_UP_TOTAL_MIN",
    ]

    print("\nBreakout and follow-up statistics:")
    print(
        breakouts[season_stat_cols]
        .head(20)
        .round(3)
        .to_string(index=False)
    )


def summarize_dimensions(
    breakouts: pd.DataFrame,
    performance_metrics: list[str],
) -> pd.DataFrame:
    """Summarize retention for each breakout dimension."""
    rows = []

    for metric in performance_metrics:
        qualified = breakouts[
            breakouts[f"QUALIFIED_{metric}"]
        ]

        retention = qualified[f"RETENTION_{metric}"]

        sustained = retention >= 0.8
        improved = retention > 1

        rows.append({
            "DIMENSION": metric,
            "COUNT": len(qualified),
            "MEDIAN_RETENTION": retention.median(),
            "PERCENT_SUSTAINED": sustained.mean() * 100,
            "PERCENT_IMPROVED": improved.mean() * 100,
        })

    return pd.DataFrame(rows)


def summarize_groups(
    breakouts: pd.DataFrame,
    group_col: str,
) -> pd.DataFrame:
    """Summarize retention and sustainability by a grouping column."""
    summary = (
        breakouts.groupby(group_col)
        .agg({
            "PLAYER_ID": "count",
            "AVERAGE_RETENTION": "median",
            "SUSTAINED_OR_IMPROVED": "mean",
        })
        .reset_index()
    )

    summary = summary.rename(columns={
        "PLAYER_ID": "COUNT",
        "AVERAGE_RETENTION": "MEDIAN_RETENTION",
        "SUSTAINED_OR_IMPROVED": "SUSTAINABILITY_RATE",
    })

    summary["SUSTAINABILITY_RATE"] = (
        summary["SUSTAINABILITY_RATE"] * 100
    )

    return summary.sort_values(
        "MEDIAN_RETENTION",
        ascending=False,
    )


def add_player_characteristics(
    breakouts: pd.DataFrame,
) -> pd.DataFrame:
    """Attach age, position, size, draft, and experience information."""
    advanced = pd.read_csv(
        "/Users/sidharthshyam/nba-breakout-project/data/raw/"
        "player_stats_advanced_rs.csv",
        usecols=["PLAYER_ID", "SEASON", "AGE"],
    )

    player_info = pd.read_csv(
        "/Users/sidharthshyam/nba-breakout-project/data/raw/"
        "player_index.csv",
        usecols=[
            "PERSON_ID",
            "POSITION",
            "HEIGHT",
            "WEIGHT",
            "DRAFT_YEAR",
            "DRAFT_ROUND",
            "DRAFT_NUMBER",
            "FROM_YEAR",
        ],
    )

    player_info = player_info.rename(
        columns={"PERSON_ID": "PLAYER_ID"}
    )

    breakouts = breakouts.merge(
        advanced,
        on=["PLAYER_ID", "SEASON"],
        how="left",
        validate="one_to_one",
    )

    return breakouts.merge(
        player_info,
        on="PLAYER_ID",
        how="left",
        validate="many_to_one",
    )


def height_to_inches(height: str) -> float:
    """Convert a height such as 6-3 into total inches."""
    if pd.isna(height):
        return np.nan

    feet, inches = height.split("-")
    return int(feet) * 12 + int(inches)


def add_characteristic_groups(
    breakouts: pd.DataFrame,
) -> pd.DataFrame:
    """Create categories used to compare player characteristics."""
    breakouts = breakouts.copy()

    breakouts["HEIGHT_INCHES"] = breakouts["HEIGHT"].apply(
        height_to_inches
    )
    breakouts["EXPERIENCE"] = (
        breakouts["SEASON_START"] - breakouts["FROM_YEAR"]
    )

    breakouts["AGE_GROUP"] = pd.cut(
        breakouts["AGE"],
        bins=[0, 22, 25, 28, 100],
        labels=[
            "22 or younger",
            "23-25",
            "26-28",
            "29 or older",
        ],
    )

    breakouts["EXPERIENCE_GROUP"] = pd.cut(
        breakouts["EXPERIENCE"],
        bins=[-1, 2, 5, 100],
        labels=["0-2 years", "3-5 years", "6+ years"],
    )

    draft_groups = []
    for draft_number in breakouts["DRAFT_NUMBER"]:
        if pd.isna(draft_number):
            draft_groups.append("Undrafted")
        elif draft_number <= 14:
            draft_groups.append("Lottery")
        elif draft_number <= 30:
            draft_groups.append("Rest of first round")
        else:
            draft_groups.append("Second round")

    breakouts["DRAFT_GROUP"] = draft_groups

    position_names = {
        "G": "Guard",
        "F": "Forward",
        "C": "Center",
    }
    position_groups = []

    for position in breakouts["POSITION"]:
        if pd.isna(position):
            position_groups.append("Unknown")
        else:
            primary_position = position.split("-")[0]
            position_groups.append(
                position_names[primary_position]
            )

    breakouts["POSITION_GROUP"] = position_groups

    return breakouts


def summarize_physical_characteristics(
    breakouts: pd.DataFrame,
) -> pd.DataFrame:
    """Compare median height and weight across sustainability outcomes."""
    return (
        breakouts.groupby("SUSTAINABILITY_RESULT")
        .agg({
            "PLAYER_ID": "count",
            "HEIGHT_INCHES": "median",
            "WEIGHT": "median",
        })
        .reset_index()
        .rename(columns={"PLAYER_ID": "COUNT"})
    )


def plot_characteristic_summaries(
    age_summary: pd.DataFrame,
    experience_summary: pd.DataFrame,
    position_summary: pd.DataFrame,
    draft_summary: pd.DataFrame,
) -> None:
    """Create RQ3 sustainability-rate plots for player characteristics."""
    summaries = [
        (age_summary, "AGE_GROUP", "Age Group"),
        (experience_summary, "EXPERIENCE_GROUP", "NBA Experience"),
        (position_summary, "POSITION_GROUP", "Position"),
        (draft_summary, "DRAFT_GROUP", "Draft Group"),
    ]

    figure, axes = plt.subplots(2, 2, figsize=(14, 10))

    for axis, (summary, group_col, title) in zip(
        axes.flatten(), summaries
    ):
        sns.barplot(
            data=summary,
            x=group_col,
            y="SUSTAINABILITY_RATE",
            ax=axis,
        )
        axis.set_title(f"Sustainability Rate by {title}")
        axis.set_xlabel(title)
        axis.set_ylabel("Sustained or Improved (%)")
        axis.tick_params(axis="x", rotation=20)
        axis.set_ylim(0, 60)

    figure.tight_layout()
    figure.savefig(
        "/Users/sidharthshyam/nba-breakout-project/figures/"
        "sustainability_by_player_characteristics.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(figure)


def plot_visualizations(
    profile_summary: pd.DataFrame,
    dimension_summary: pd.DataFrame,
    dimension_count_summary: pd.DataFrame,
) -> None:

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=dimension_summary,
        x="DIMENSION",
        y="MEDIAN_RETENTION",
    )
    plt.axhline(
        y=0.8,
        color="red",
        linestyle="--",
        label="80% sustainability threshold",
    )
    plt.title(
        "Median Breakout Improvement Retained "
        "by Performance Dimension"
    )
    plt.xlabel("Performance Dimension")
    plt.ylabel("Median Improvement Retained")
    plt.legend()
    plt.savefig(
        "/Users/sidharthshyam/nba-breakout-project/figures/"
        "median_retention_by_dimension.png",
        dpi=300,
    )

    plt.close()

    plt.figure(figsize=(11, 7))

    sns.barplot(
        data=profile_summary,
        x="SUSTAINABILITY_RATE",
        y="BREAKOUT_PROFILE",
    )
    plt.title("Sustainability Rate by Breakout Profile")
    plt.xlabel("Breakouts Sustained or Improved (%)")
    plt.ylabel("Breakout Profile")

    plt.savefig(
        "/Users/sidharthshyam/nba-breakout-project/figures/"
        "sustainability_rate_by_profile.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    plt.figure(figsize=(8, 6))

    sns.barplot(
        data=dimension_count_summary,
        x="BREAKOUT_DIMENSIONS",
        y="SUSTAINABILITY_RATE",
    )

    plt.title(
        "Breakout Sustainability Rate "
        "by Number of Improved Dimensions"
    )
    plt.xlabel("Number of Qualifying Breakout Dimensions")
    plt.ylabel("Breakouts Sustained or Improved (%)")
    plt.ylim(0, 50)

    plt.savefig(
        "/Users/sidharthshyam/nba-breakout-project/figures/"
        "sustainability_rate_by_dimension_count.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


def main() -> None:
    """Run the complete breakout sustainability analysis."""
    stats = ba.load_and_merge(ba.DEFAULT_DATA_DIR)

    pairs, performance_metrics = ba.find_breakouts(
        stats,
        minute_cutoff=ba.MINUTE_CUTOFF,
        percentile_threshold=ba.PERCENTILE_THRESHOLD,
        min_dimensions=ba.MIN_DIMENSIONS,
    )

    breakouts = pairs[pairs["IS_BREAKOUT"]].copy()

    breakouts = add_following_season(
        breakouts,
        stats,
        performance_metrics,
    )

    breakouts = filter_eligible_follow_ups(
        breakouts,
        ba.MINUTE_CUTOFF,
    )

    breakouts = calculate_retention(
        breakouts,
        performance_metrics,
    )

    retention_cols = []

    for metric in performance_metrics:
        retention_cols.append(f"RETENTION_{metric}")

    breakouts = classify_sustainability(
        breakouts,
        retention_cols,
    )

    breakouts = add_player_characteristics(
        breakouts,
    )

    breakouts = add_characteristic_groups(breakouts)

    # Research Question 1 results
    sustainability_summary = create_summary(breakouts)

    # Research Question 2: individual performance dimensions
    dimension_summary = summarize_dimensions(
        breakouts,
        performance_metrics,
    )

    # Research Question 2: combinations of performance dimensions
    profile_summary = summarize_groups(
        breakouts,
        "BREAKOUT_PROFILE",
    )

    # Only report profiles with at least 10 observations.
    common_profiles = profile_summary[
        profile_summary["COUNT"] >= 10
    ].copy()

    # Research Question 2: number of qualifying dimensions
    dimension_count_summary = summarize_groups(
        breakouts,
        "BREAKOUT_DIMENSIONS",
    )

    # Research Question 3: player characteristics
    age_summary = summarize_groups(
        breakouts,
        "AGE_GROUP",
    )

    experience_summary = summarize_groups(
        breakouts,
        "EXPERIENCE_GROUP",
    )

    position_summary = summarize_groups(
        breakouts,
        "POSITION_GROUP",
    )

    draft_summary = summarize_groups(
        breakouts,
        "DRAFT_GROUP",
    )

    physical_summary = summarize_physical_characteristics(
        breakouts
    )

    plot_visualizations(
        common_profiles,
        dimension_summary,
        dimension_count_summary,
    )

    plot_characteristic_summaries(
        age_summary,
        experience_summary,
        position_summary,
        draft_summary,
    )

    print_results(
        breakouts,
        sustainability_summary,
        retention_cols,
    )

    print("\nRetention by individual breakout dimension:")
    print(
        dimension_summary
        .round(3)
        .to_string(index=False)
    )

    print("\nRetention by common breakout profile:")
    print(
        common_profiles
        .round(3)
        .to_string(index=False)
    )

    print("\nRetention by number of breakout dimensions:")
    print(
        dimension_count_summary
        .round(3)
        .to_string(index=False)
    )

    print("\nSustainability by age group:")
    print(age_summary.round(3).to_string(index=False))

    print("\nSustainability by NBA experience:")
    print(experience_summary.round(3).to_string(index=False))

    print("\nSustainability by position:")
    print(position_summary.round(3).to_string(index=False))

    print("\nSustainability by draft group:")
    print(draft_summary.round(3).to_string(index=False))

    print("\nPhysical characteristics by sustainability result:")
    print(physical_summary.round(3).to_string(index=False))

    # Save the complete player-level dataset.
    breakouts.to_csv(
        "nba_breakout_sustainability.csv",
        index=False,
    )

    # Save Research Question 1 results.
    sustainability_summary.to_csv(
        "sustainability_summary.csv",
        index=False,
    )

    # Save Research Question 2 results.
    dimension_summary.to_csv(
        "dimension_summary.csv",
        index=False,
    )

    common_profiles.to_csv(
        "profile_summary.csv",
        index=False,
    )

    dimension_count_summary.to_csv(
        "dimension_count_summary.csv",
        index=False,
    )

    # Save Research Question 3 results.
    age_summary.to_csv(
        "age_summary.csv",
        index=False,
    )

    experience_summary.to_csv(
        "experience_summary.csv",
        index=False,
    )

    position_summary.to_csv(
        "position_summary.csv",
        index=False,
    )

    draft_summary.to_csv(
        "draft_summary.csv",
        index=False,
    )

    physical_summary.to_csv(
        "physical_summary.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
