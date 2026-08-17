"""Simple NBA breakout-season finder."""

import pandas as pd


MINUTE_CUTOFF = 500
PERCENTILE_THRESHOLD = 0.85
MIN_DIMENSIONS = 2


def load_and_merge() -> pd.DataFrame:
    """Load the three season-level CSV files
      and merge them by player
      and season."""
    advanced = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/"
                           "raw/player_stats_advanced_rs.csv")
    traditional = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data"
                              "/raw/player_stats_traditionnal_rs.csv")
    usage = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/"
                        "player_stats_usage_rs.csv")

    keys = ["PLAYER_ID", "SEASON"]

    # Traditional PTS and MIN are per-game values in these files.
    traditional_cols = keys + ["PLAYER_NAME", "TEAM_ABBREVIATION",
                               "GP", "MPG", "PTS"]
    traditional = traditional[traditional_cols]

    # Advanced contains the performance-rate statistics used by the definition.
    advanced = advanced[keys + ["TS_PCT", "AST_PCT", "REB_PCT"]]

    # Usage-file MIN is total minutes, unlike MIN in the other two files.
    usage = usage[keys + ["TOTAL_MIN", "USG_PCT"]]

    merged = traditional.merge(advanced, on=keys, how="inner",
                               validate="one_to_one")
    merged = merged.merge(usage, on=keys, how="inner", validate="one_to_one")
    merged["PTS_PER_36"] = merged["PTS"] / merged["MPG"] * 36
    merged["SEASON_START"] = merged["SEASON"].str[:4].astype(int)
    merged = merged[merged["SEASON_START"] >= 2000]
    return merged.sort_values(["PLAYER_ID", "SEASON_START"])


def find_breakouts(
    stats: pd.DataFrame,
    minute_cutoff: int = 500,
    percentile_threshold: float = 0.85,
    min_dimensions: int = 2,
) -> tuple[pd.DataFrame, list[str]]:
    """Create consecutive season pairs and classify breakout player-seasons."""
    previous = stats.groupby("PLAYER_ID").shift(1)
    pairs = stats.copy()
    pairs["PREV_SEASON"] = previous["SEASON"]
    pairs["PREV_TOTAL_MIN"] = previous["TOTAL_MIN"]

    consecutive = (pairs["SEASON_START"] - previous["SEASON_START"] == 1)
    enough_minutes = (
        (pairs["TOTAL_MIN"] >= minute_cutoff)
        & (pairs["PREV_TOTAL_MIN"] >= minute_cutoff)
    )
    pairs = pairs[consecutive & enough_minutes].copy()
    performance_metrics = ["PTS_PER_36", "TS_PCT", "AST_PCT", "REB_PCT"]

    qualified_cols = []
    for metric in performance_metrics:
        change_col = f"DELTA_{metric}"
        percentile_col = f"PCTL_{metric}"
        qualified_col = f"QUALIFIED_{metric}"
        pairs[f"PREV_{metric}"] = previous[metric]
        pairs[change_col] = pairs[metric] - previous[metric]
        pairs[percentile_col] = pairs.groupby("SEASON")[change_col].rank(
            pct=True)
        pairs[qualified_col] = (
            pairs[percentile_col] >= percentile_threshold
        )

        qualified_cols.append(qualified_col)

    pairs["BREAKOUT_DIMENSIONS"] = (
        pairs[qualified_cols].sum(axis=1)
    )

    pairs["IS_BREAKOUT"] = (
        pairs["BREAKOUT_DIMENSIONS"] >= min_dimensions
    )

    profiles = []

    for index in pairs.index:
        qualified_metrics = []

        for metric in performance_metrics:
            if pairs.at[index, f"QUALIFIED_{metric}"]:
                qualified_metrics.append(metric)

        profiles.append(" + ".join(qualified_metrics))

    pairs["BREAKOUT_PROFILE"] = profiles

    for metric in ["MPG", "USG_PCT"]:
        pairs[f"PREV_{metric}"] = previous[metric]

        pairs[f"DELTA_{metric}"] = (
            pairs[metric] - previous[metric]
        )

    return pairs, performance_metrics


def main() -> None:
    """Run the breakout analysis, display a summary, and save the results."""
    stats = load_and_merge()

    pairs, performance_metrics = find_breakouts(
        stats,
        minute_cutoff=MINUTE_CUTOFF,
        percentile_threshold=PERCENTILE_THRESHOLD,
        min_dimensions=MIN_DIMENSIONS,
    )

    breakouts = pairs[pairs["IS_BREAKOUT"]].copy()

    result_cols = [
        "PLAYER_ID",
        "PLAYER_NAME",
        "PREV_SEASON",
        "SEASON",
        "TEAM_ABBREVIATION",
        "PREV_TOTAL_MIN",
        "TOTAL_MIN",
        "PREV_MPG",
        "MPG",
        "DELTA_MPG",
        "PREV_USG_PCT",
        "USG_PCT",
        "DELTA_USG_PCT",
        "BREAKOUT_DIMENSIONS",
    ]

    for metric in performance_metrics:
        result_cols.extend([
            f"PREV_{metric}",
            metric,
            f"DELTA_{metric}",
            f"PCTL_{metric}",
        ])

    breakouts = breakouts[result_cols].sort_values(
        by=["SEASON", "BREAKOUT_DIMENSIONS", "PLAYER_NAME"],
        ascending=[True, False, True],
    )

    output_path = "nba_breakout_seasons.csv"
    breakouts.to_csv(output_path, index=False)

    print(f"Eligible player-season pairs: {len(pairs)}")
    print(f"Breakout seasons found: {len(breakouts)}")
    print(f"Minute cutoff: {MINUTE_CUTOFF}")
    print(f"Percentile threshold: {PERCENTILE_THRESHOLD:.0%}")
    print(f"Required dimensions: {MIN_DIMENSIONS}")
    print(f"Metrics used: {', '.join(performance_metrics)}")
    print(f"Results saved to: {output_path}")

    if not breakouts.empty:
        print("\nFirst 20 breakout seasons:")

        display_cols = [
            "PLAYER_NAME",
            "PREV_SEASON",
            "SEASON",
            "PREV_PTS_PER_36",
            "PTS_PER_36",
            "DELTA_PTS_PER_36",
            "PREV_TS_PCT",
            "TS_PCT",
            "DELTA_TS_PCT",
            "PREV_AST_PCT",
            "AST_PCT",
            "DELTA_AST_PCT",
            "PREV_REB_PCT",
            "REB_PCT",
            "DELTA_REB_PCT",
            "BREAKOUT_DIMENSIONS",
        ]

        print(
            breakouts[display_cols]
            .head(20)
            .round(3)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
