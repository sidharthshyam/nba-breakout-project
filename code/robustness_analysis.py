"""Run robustness checks for the NBA breakout sustainability study."""

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

import ba
import sa


CODE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CODE_DIR / "robustness_outputs"
BOOTSTRAP_SAMPLES = 2000
RANDOM_SEED = 163


def prepare_breakout_samples(
    stats: pd.DataFrame,
    minute_cutoff: int,
    percentile_threshold: float,
    min_dimensions: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Create all detected breakouts and the eligible follow-up sample."""
    pairs, performance_metrics = ba.find_breakouts(
        stats,
        minute_cutoff=minute_cutoff,
        percentile_threshold=percentile_threshold,
        min_dimensions=min_dimensions,
    )

    all_breakouts = pairs[pairs["IS_BREAKOUT"]].copy()
    all_breakouts = sa.add_following_season(
        all_breakouts,
        stats,
        performance_metrics,
    )

    eligible = sa.filter_eligible_follow_ups(
        all_breakouts,
        minute_cutoff,
    )
    eligible = sa.calculate_retention(
        eligible,
        performance_metrics,
    )

    retention_cols = [
        f"RETENTION_{metric}"
        for metric in performance_metrics
    ]
    eligible["AVERAGE_RETENTION"] = (
        eligible[retention_cols].mean(axis=1)
    )

    return all_breakouts, eligible, performance_metrics


def create_attrition_summary(
    all_breakouts: pd.DataFrame,
    eligible: pd.DataFrame,
    minute_cutoff: int,
    retention_threshold: float = 0.80,
) -> pd.DataFrame:
    """Describe outcomes for every breakout, including missing follow-ups."""
    outcomes = all_breakouts[["PLAYER_ID", "SEASON"]].copy()
    outcomes["OUTCOME"] = "No following-season record"

    has_follow_up = all_breakouts["FOLLOW_UP_SEASON"].notna()
    below_cutoff = (
        has_follow_up
        & (all_breakouts["FOLLOW_UP_TOTAL_MIN"] < minute_cutoff)
    )
    outcomes.loc[below_cutoff, "OUTCOME"] = (
        f"Following season below {minute_cutoff} minutes"
    )

    retention = eligible.set_index(
        ["PLAYER_ID", "SEASON"]
    )["AVERAGE_RETENTION"]
    eligible_keys = pd.MultiIndex.from_frame(
        outcomes[["PLAYER_ID", "SEASON"]]
    )
    outcomes["AVERAGE_RETENTION"] = retention.reindex(
        eligible_keys
    ).to_numpy()

    eligible_mask = outcomes["AVERAGE_RETENTION"].notna()
    sustained = (
        eligible_mask
        & (outcomes["AVERAGE_RETENTION"] >= retention_threshold)
    )
    outcomes.loc[eligible_mask, "OUTCOME"] = (
        "Eligible follow-up: regressed"
    )
    outcomes.loc[sustained, "OUTCOME"] = (
        "Eligible follow-up: sustained or improved"
    )

    summary = outcomes["OUTCOME"].value_counts().reset_index()
    summary.columns = ["OUTCOME", "COUNT"]
    summary["PERCENT_OF_ALL_BREAKOUTS"] = (
        summary["COUNT"] / len(outcomes) * 100
    )
    return summary


def summarize_repeat_players(
    all_breakouts: pd.DataFrame,
    eligible: pd.DataFrame,
) -> pd.DataFrame:
    """Report how often the same player contributes multiple breakouts."""
    rows = []

    for sample_name, sample in [
        ("All detected breakouts", all_breakouts),
        ("Eligible follow-ups", eligible),
    ]:
        counts = sample["PLAYER_ID"].value_counts()
        repeated_players = int((counts > 1).sum())
        rows.append({
            "SAMPLE": sample_name,
            "BREAKOUT_SEASONS": len(sample),
            "UNIQUE_PLAYERS": sample["PLAYER_ID"].nunique(),
            "PLAYERS_WITH_MULTIPLE_BREAKOUTS": repeated_players,
            "PERCENT_PLAYERS_WITH_MULTIPLE_BREAKOUTS": (
                repeated_players / len(counts) * 100
                if len(counts) > 0 else np.nan
            ),
        })

    return pd.DataFrame(rows)


def player_cluster_bootstrap_ci(
    data: pd.DataFrame,
    outcome_col: str,
    samples: int = BOOTSTRAP_SAMPLES,
    seed: int = RANDOM_SEED,
) -> tuple[float, float, float]:
    """Estimate a mean and 95% CI by resampling whole players."""
    player_values = (
        data.groupby("PLAYER_ID", observed=True)[outcome_col]
        .agg(["sum", "count"])
        .dropna()
    )

    if player_values.empty:
        return np.nan, np.nan, np.nan

    rng = np.random.default_rng(seed)
    bootstrap_estimates = []

    for _ in range(samples):
        sampled = rng.integers(
            0,
            len(player_values),
            size=len(player_values),
        )
        sampled_values = player_values.iloc[sampled]
        estimate = (
            sampled_values["sum"].sum()
            / sampled_values["count"].sum()
        )
        bootstrap_estimates.append(estimate)

    estimate = data[outcome_col].mean()
    lower, upper = np.quantile(
        bootstrap_estimates,
        [0.025, 0.975],
    )
    return estimate, lower, upper


def create_confidence_interval_summary(
    breakouts: pd.DataFrame,
    group_cols: list[str],
) -> pd.DataFrame:
    """Create player-clustered intervals overall and by player groups."""
    rows = []

    estimate, lower, upper = player_cluster_bootstrap_ci(
        breakouts,
        "SUSTAINED_OR_IMPROVED",
    )
    rows.append({
        "VARIABLE": "Overall",
        "GROUP": "All eligible breakouts",
        "COUNT": len(breakouts),
        "RATE": estimate * 100,
        "CI_LOWER": lower * 100,
        "CI_UPPER": upper * 100,
    })

    for group_col in group_cols:
        grouped = breakouts.dropna(subset=[group_col]).groupby(
            group_col,
            observed=True,
        )
        for group_name, group in grouped:
            estimate, lower, upper = player_cluster_bootstrap_ci(
                group,
                "SUSTAINED_OR_IMPROVED",
            )
            rows.append({
                "VARIABLE": group_col,
                "GROUP": str(group_name),
                "COUNT": len(group),
                "RATE": estimate * 100,
                "CI_LOWER": lower * 100,
                "CI_UPPER": upper * 100,
            })

    return pd.DataFrame(rows)


def summarize_alternative_outcome(
    breakouts: pd.DataFrame,
    performance_metrics: list[str],
) -> pd.DataFrame:
    """Summarize direct follow-up minus breakout changes by dimension."""
    rows = []

    for metric in performance_metrics:
        qualified = breakouts[f"QUALIFIED_{metric}"]
        change = (
            breakouts.loc[qualified, f"FOLLOW_UP_{metric}"]
            - breakouts.loc[qualified, metric]
        )
        rows.append({
            "DIMENSION": metric,
            "COUNT": len(change),
            "MEDIAN_FOLLOW_UP_MINUS_BREAKOUT": change.median(),
            "PERCENT_MAINTAINED_OR_IMPROVED": (
                (change >= 0).mean() * 100
            ),
        })

    return pd.DataFrame(rows)


def summarize_breakout_denominators(
    breakouts: pd.DataFrame,
    performance_metrics: list[str],
) -> pd.DataFrame:
    """Describe the original improvements used as retention denominators."""
    rows = []

    for metric in performance_metrics:
        changes = breakouts.loc[
            breakouts[f"QUALIFIED_{metric}"],
            f"DELTA_{metric}",
        ]
        rows.append({
            "DIMENSION": metric,
            "COUNT": len(changes),
            "MIN": changes.min(),
            "Q1": changes.quantile(0.25),
            "MEDIAN": changes.median(),
            "Q3": changes.quantile(0.75),
            "MAX": changes.max(),
        })

    return pd.DataFrame(rows)


def run_sensitivity_analysis(
    stats: pd.DataFrame,
    minute_cutoffs: list[int],
    percentile_thresholds: list[float],
    dimension_requirements: list[int],
    retention_thresholds: list[float],
) -> pd.DataFrame:
    """Rerun the analysis over a grid of defensible definitions."""
    rows = []

    breakout_settings = product(
        minute_cutoffs,
        percentile_thresholds,
        dimension_requirements,
    )

    for minute_cutoff, percentile_threshold, min_dimensions in (
        breakout_settings
    ):
        all_breakouts, eligible, _ = prepare_breakout_samples(
            stats,
            minute_cutoff,
            percentile_threshold,
            min_dimensions,
        )

        for retention_threshold in retention_thresholds:
            sustained = (
                eligible["AVERAGE_RETENTION"]
                >= retention_threshold
            )
            rows.append({
                "MINUTE_CUTOFF": minute_cutoff,
                "PERCENTILE_THRESHOLD": percentile_threshold,
                "MIN_DIMENSIONS": min_dimensions,
                "RETENTION_THRESHOLD": retention_threshold,
                "BREAKOUTS_FOUND": len(all_breakouts),
                "BREAKOUTS_WITH_ANY_FOLLOW_UP": (
                    all_breakouts["FOLLOW_UP_SEASON"].notna().sum()
                ),
                "ELIGIBLE_FOLLOW_UPS": len(eligible),
                "UNIQUE_PLAYERS": eligible["PLAYER_ID"].nunique(),
                "MEDIAN_RETENTION": (
                    eligible["AVERAGE_RETENTION"].median()
                ),
                "SUSTAINABILITY_RATE": sustained.mean() * 100,
            })

    return pd.DataFrame(rows)


def main() -> None:
    """Run and save all publication-oriented robustness checks."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    stats = ba.load_and_merge()

    all_breakouts, eligible, performance_metrics = (
        prepare_breakout_samples(
            stats,
            ba.MINUTE_CUTOFF,
            ba.PERCENTILE_THRESHOLD,
            ba.MIN_DIMENSIONS,
        )
    )

    eligible["SUSTAINED_OR_IMPROVED"] = (
        eligible["AVERAGE_RETENTION"] >= 0.80
    )

    attrition = create_attrition_summary(
        all_breakouts,
        eligible,
        ba.MINUTE_CUTOFF,
    )
    repeat_players = summarize_repeat_players(
        all_breakouts,
        eligible,
    )
    alternative_outcomes = summarize_alternative_outcome(
        eligible,
        performance_metrics,
    )
    denominator_summary = summarize_breakout_denominators(
        eligible,
        performance_metrics,
    )

    characteristics = sa.add_player_characteristics(eligible)
    characteristics = sa.add_characteristic_groups(characteristics)
    confidence_intervals = create_confidence_interval_summary(
        characteristics,
        [
            "AGE_GROUP",
            "EXPERIENCE_GROUP",
            "POSITION_GROUP",
            "DRAFT_GROUP",
        ],
    )

    sensitivity = run_sensitivity_analysis(
        stats,
        minute_cutoffs=[500, 750, 1000],
        percentile_thresholds=[0.80, 0.85, 0.90],
        dimension_requirements=[2, 3],
        retention_thresholds=[0.70, 0.80, 0.90],
    )

    outputs = {
        "attrition_summary.csv": attrition,
        "repeat_player_summary.csv": repeat_players,
        "confidence_intervals.csv": confidence_intervals,
        "alternative_outcome_summary.csv": alternative_outcomes,
        "retention_denominator_summary.csv": denominator_summary,
        "sensitivity_analysis.csv": sensitivity,
    }

    for filename, data in outputs.items():
        data.to_csv(OUTPUT_DIR / filename, index=False)

    print("\nAttrition outcomes for all detected breakouts:")
    print(attrition.round(2).to_string(index=False))
    print("\nRepeated-player summary:")
    print(repeat_players.round(2).to_string(index=False))
    print("\nPlayer-clustered 95% confidence intervals:")
    print(confidence_intervals.round(2).to_string(index=False))
    print("\nAlternative follow-up minus breakout outcome:")
    print(alternative_outcomes.round(3).to_string(index=False))
    print("\nSensitivity-analysis ranges:")
    print(
        sensitivity[
            [
                "BREAKOUTS_FOUND",
                "ELIGIBLE_FOLLOW_UPS",
                "MEDIAN_RETENTION",
                "SUSTAINABILITY_RATE",
            ]
        ].agg(["min", "max"]).round(3)
    )
    print(f"\nResults saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
