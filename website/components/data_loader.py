"""Read existing research outputs; never run or overwrite the research pipeline."""

from pathlib import Path
import math

import pandas as pd
import streamlit as st

WEBSITE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = WEBSITE_DIR.parent
CODE_DIR = PROJECT_DIR / "code"
RAW_DIR = PROJECT_DIR / "data" / "raw"
GITHUB_URL = "https://github.com/sidharthshyam/nba-breakout-project"
DATA_SOURCE_URL = "https://github.com/Brescou/NBA-dataset-stats-player-team"
BASELINE = (500, 0.85, 2, 0.80)
KEYS = ["PLAYER_ID", "SEASON"]
METRICS = {
    "PTS_PER_36": ("Scoring", "Points per 36", "#8B3A2B"),
    "TS_PCT": ("Efficiency", "True shooting %", "#8B3A2B"),
    "AST_PCT": ("Playmaking", "Assist %", "#8B3A2B"),
    "REB_PCT": ("Rebounding", "Rebound %", "#8B3A2B"),
}
OUTCOMES = ["Regressed", "Sustained at least 80%", "Improved further"]
SENSITIVITY_KEYS = ["MINUTE_CUTOFF", "PERCENTILE_THRESHOLD", "MIN_DIMENSIONS", "RETENTION_THRESHOLD"]
FILES = {
    "breakouts": "nba_breakout_seasons.csv",
    "eligible": "nba_breakout_sustainability.csv",
    "outcomes": "sustainability_summary.csv",
    "dimensions": "dimension_summary.csv",
    "profiles": "profile_summary.csv",
    "dimension_counts": "dimension_count_summary.csv",
    "age": "age_summary.csv",
    "experience": "experience_summary.csv",
    "position": "position_summary.csv",
    "draft": "draft_summary.csv",
    "physical": "physical_summary.csv",
    "sensitivity": "robustness_outputs/sensitivity_analysis.csv",
    "attrition": "robustness_outputs/attrition_summary.csv",
    "intervals": "robustness_outputs/confidence_intervals.csv",
}


def require_columns(data: pd.DataFrame, columns: list[str], source: str) -> None:
    """Raise an actionable error when a required input is incomplete."""
    missing = sorted(set(columns) - set(data.columns))
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")


@st.cache_data(ttl=300, show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    """Load a saved research table with a five-minute cache."""
    path = CODE_DIR / FILES[name]
    if not path.is_file():
        raise FileNotFoundError(f"Missing research output: code/{FILES[name]}. See website/README.md.")
    data = pd.read_csv(path)
    if name in {"breakouts", "eligible"}:
        require_columns(data, KEYS + ["PLAYER_NAME", "BREAKOUT_DIMENSIONS"], path.name)
        if data.duplicated(KEYS).any():
            raise ValueError(f"Duplicate player-season keys in {path.name}.")
    if name == "eligible":
        require_columns(data, ["AVERAGE_RETENTION", "SUSTAINABILITY_RESULT", "FOLLOW_UP_SEASON", "FOLLOW_UP_TOTAL_MIN", "BREAKOUT_PROFILE"], path.name)
        if data["AVERAGE_RETENTION"].isna().any():
            raise ValueError("The eligible results contain missing average retention.")
    if name == "sensitivity":
        require_columns(data, SENSITIVITY_KEYS + ["BREAKOUTS_FOUND", "BREAKOUTS_WITH_ANY_FOLLOW_UP", "ELIGIBLE_FOLLOW_UPS", "SUSTAINABILITY_RATE"], path.name)
        if data.duplicated(SENSITIVITY_KEYS).any():
            raise ValueError("Sensitivity settings must identify exactly one row.")
        data["SUSTAINED_COUNT"] = data.apply(sustained_count, axis=1)
    return data


def sustained_count(row: pd.Series) -> int:
    """Recover an integer count from a full-precision percentage and its denominator."""
    value = row["SUSTAINABILITY_RATE"] * row["ELIGIBLE_FOLLOW_UPS"] / 100
    count = round(value)
    if not math.isclose(value, count, abs_tol=1e-6):
        raise ValueError("Sensitivity rate does not resolve to an integer outcome count.")
    if not 0 <= count <= row["ELIGIBLE_FOLLOW_UPS"]:
        raise ValueError("Sensitivity outcome count is outside its sample size.")
    return count


def select_specification(data: pd.DataFrame, minutes: int, percentile: float,
                         dimensions: int, retention: float) -> pd.Series:
    """Select one of the precomputed sensitivity specifications."""
    mask = (data["MINUTE_CUTOFF"] == minutes) & (data["MIN_DIMENSIONS"] == dimensions)
    mask &= (data["PERCENTILE_THRESHOLD"] - percentile).abs() < 1e-8
    mask &= (data["RETENTION_THRESHOLD"] - retention).abs() < 1e-8
    rows = data[mask]
    if len(rows) != 1:
        raise ValueError("This definition does not have exactly one saved result.")
    return rows.iloc[0]


@st.cache_data(ttl=300, show_spinner=False)
def load_season_stats() -> pd.DataFrame:
    """Read the minimal raw columns needed for coverage and unevaluated follow-ups."""
    traditional = pd.read_csv(RAW_DIR / "player_stats_traditionnal_rs.csv",
                              usecols=KEYS + ["MPG", "PTS"])
    advanced = pd.read_csv(RAW_DIR / "player_stats_advanced_rs.csv",
                           usecols=KEYS + ["TS_PCT", "AST_PCT", "REB_PCT"])
    usage = pd.read_csv(RAW_DIR / "player_stats_usage_rs.csv",
                        usecols=lambda column: column in KEYS + ["TOTAL_MIN", "USG_PCT"])
    require_columns(usage, KEYS + ["TOTAL_MIN"], "player_stats_usage_rs.csv")
    if "USG_PCT" not in usage:
        usage["USG_PCT"] = float("nan")
    stats = traditional.merge(advanced, on=KEYS, validate="one_to_one").merge(
        usage, on=KEYS, validate="one_to_one")
    stats["SEASON_START"] = stats["SEASON"].str[:4].astype(int)
    stats["PTS_PER_36"] = stats["PTS"].div(stats["MPG"].where(stats["MPG"] > 0)) * 36
    return stats[stats["SEASON_START"] >= 2000].sort_values(["PLAYER_ID", "SEASON_START"])


@st.cache_data(ttl=300, show_spinner=False)
def baseline_numbers() -> dict:
    """Derive headline numbers from saved outputs, verifying their agreement."""
    all_breakouts, eligible = load_table("breakouts"), load_table("eligible")
    baseline = select_specification(load_table("sensitivity"), *BASELINE)
    stats = load_season_stats()
    previous = stats.groupby("PLAYER_ID").shift(1)
    valid = ((stats.SEASON_START - previous.SEASON_START) == 1)
    valid &= (stats.TOTAL_MIN >= BASELINE[0]) & (previous.TOTAL_MIN >= BASELINE[0])
    successes = int((eligible.AVERAGE_RETENTION >= BASELINE[3]).sum())
    if (len(all_breakouts) != baseline.BREAKOUTS_FOUND or
            len(eligible) != baseline.ELIGIBLE_FOLLOW_UPS or
            successes != baseline.SUSTAINED_COUNT):
        raise ValueError("Saved baseline and sensitivity results disagree. Regenerate the research outputs.")
    return {"pairs": int(valid.sum()), "breakouts": len(all_breakouts),
            "any_follow_up": int(baseline.BREAKOUTS_WITH_ANY_FOLLOW_UP),
            "eligible": len(eligible), "successes": successes,
            "rate": successes / len(eligible) * 100,
            "median_retention": eligible.AVERAGE_RETENTION.median(),
            "first_breakout": all_breakouts.SEASON.min(),
            "last_breakout": all_breakouts.SEASON.max(),
            "last_evaluated": eligible.SEASON.max()}


def readable_profile(profile: str) -> str:
    """Translate metric identifiers to basketball dimension names."""
    if pd.isna(profile) or not profile:
        return "Unavailable"
    return " + ".join(METRICS.get(part.strip(), (part.strip(),))[0]
                      for part in str(profile).split("+"))


@st.cache_data(ttl=300, show_spinner=False)
def load_explorer() -> pd.DataFrame:
    """Join all detected breakouts to saved outcomes and raw follow-up coverage."""
    detected, eligible = load_table("breakouts"), load_table("eligible")
    # Saved evaluated rows are authoritative. Retain them without recalculating outcomes.
    additions = [c for c in eligible.columns if c not in detected.columns]
    result = detected.merge(eligible[KEYS + additions], on=KEYS, how="left", validate="one_to_one")
    result["SEASON_START"] = result.SEASON.str[:4].astype(int)
    following = load_season_stats().copy()
    following["SEASON_START"] -= 1
    fields = ["SEASON", "TOTAL_MIN", "MPG", "USG_PCT"] + list(METRICS)
    following = following[["PLAYER_ID", "SEASON_START"] + fields]
    following = following.rename(columns={c: f"RAW_NEXT_{c}" for c in fields})
    result = result.merge(following, on=["PLAYER_ID", "SEASON_START"], how="left", validate="one_to_one")
    for field in fields:
        col = f"FOLLOW_UP_{field}"
        if col not in result:
            result[col] = float("nan")
        result[col] = result[col].combine_first(result[f"RAW_NEXT_{field}"])
    result = result.drop(columns=[f"RAW_NEXT_{c}" for c in fields])
    for metric in METRICS:
        result[f"QUALIFIED_{metric}"] = result[f"PCTL_{metric}"] >= BASELINE[1]
    result["BREAKOUT_PROFILE"] = result.apply(
        lambda row: " + ".join(m for m in METRICS if row[f"QUALIFIED_{m}"]), axis=1)
    result["PROFILE_LABEL"] = result.BREAKOUT_PROFILE.map(readable_profile)
    result["EVALUATED"] = result.AVERAGE_RETENTION.notna()
    result["SUSTAINABILITY_RESULT"] = result.SUSTAINABILITY_RESULT.fillna("Not evaluated")
    result["FOLLOW_UP_STATUS"] = "Eligible follow-up"
    result.loc[~result.EVALUATED, "FOLLOW_UP_STATUS"] = "Following season below 500 minutes"
    result.loc[result.FOLLOW_UP_SEASON.isna(), "FOLLOW_UP_STATUS"] = "No following-season record"
    last_year = load_season_stats().SEASON_START.max()
    result.loc[result.FOLLOW_UP_SEASON.isna() & (result.SEASON_START == last_year),
               "FOLLOW_UP_STATUS"] = "Following season outside dataset"
    return result.sort_values(["PLAYER_NAME", "SEASON"])


def filter_players(data: pd.DataFrame, seasons: list | None = None,
                   outcomes: list | None = None, profiles: list | None = None,
                   dimensions: list | None = None) -> pd.DataFrame:
    """Apply independent filters; an empty selection means all values."""
    result = data
    for col, selected in [("SEASON", seasons), ("SUSTAINABILITY_RESULT", outcomes),
                          ("PROFILE_LABEL", profiles), ("BREAKOUT_DIMENSIONS", dimensions)]:
        if selected:
            result = result[result[col].isin(selected)]
    return result.copy()


def format_metric(value: float, metric: str, change: bool = False) -> str:
    """Format rates as percentages and rate changes as percentage points."""
    if pd.isna(value):
        return "Unavailable"
    sign = "+" if change and value > 0 else ""
    if metric.endswith("PCT"):
        return f"{sign}{value * 100:.1f}{' pp' if change else '%'}"
    return f"{sign}{value:.2f}"


def dimension_table(row: pd.Series) -> pd.DataFrame:
    """Build a readable player table; tolerate missing optional follow-up fields."""
    records = []
    for metric, (dimension, label, _) in METRICS.items():
        percentile = row.get(f"PCTL_{metric}", float("nan"))
        retention = row.get(f"RETENTION_{metric}", float("nan"))
        records.append({"Dimension": dimension, "Metric": label,
                        "Previous": format_metric(row.get(f"PREV_{metric}"), metric),
                        "Breakout": format_metric(row.get(metric), metric),
                        "Following": format_metric(row.get(f"FOLLOW_UP_{metric}"), metric),
                        "Improvement": format_metric(row.get(f"DELTA_{metric}"), metric, True),
                        "Percentile": f"{percentile * 100:.1f}" if pd.notna(percentile) else "Unavailable",
                        "Qualified": "Yes" if row.get(f"QUALIFIED_{metric}", False) else "No",
                        "Retention": f"{retention:.1%}" if pd.notna(retention) else "Not evaluated"})
    return pd.DataFrame(records)


def player_interpretation(row: pd.Series) -> str:
    """Describe the selected observation without making causal claims."""
    profile = row["PROFILE_LABEL"].lower().replace(" + ", ", ")
    if pd.isna(row.get("AVERAGE_RETENTION")):
        return f"This season qualified through {profile}. Sustainability was not evaluated: {row['FOLLOW_UP_STATUS'].lower()}."
    return (f"This season qualified through {profile}. The average retention across those qualifying "
            f"dimensions was {row['AVERAGE_RETENTION']:.1%}. The saved classification is "
            f"“{row['SUSTAINABILITY_RESULT']}.”")


def paper_path() -> Path | None:
    """Find the included manuscript without referencing a developer's computer."""
    for name in ["nba_breakout_paper_with_sensitivity.pdf", "nba_breakout_paper_with_sensitivity.docx"]:
        path = WEBSITE_DIR / "assets" / name
        if path.is_file():
            return path
    return None
