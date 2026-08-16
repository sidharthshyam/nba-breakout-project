"""Simple tests for the NBA breakout sustainability project."""

import numpy as np
import pandas as pd

import ba
import sa as sa


TEST_DATA = (
    "/Users/sidharthshyam/nba-breakout-project/"
    "data/test/test_stats.csv"
)


def test_find_breakouts() -> None:
    """Test season pairing, minute eligibility, and breakout dimensions."""
    stats = pd.read_csv(TEST_DATA)

    pairs, metrics = ba.find_breakouts(
        stats,
        minute_cutoff=500,
        percentile_threshold=0.90,
        min_dimensions=2,
    )

    assert set(pairs["PLAYER_ID"]) == {1, 2, 3}
    assert metrics == ["PTS_PER_36", "TS_PCT", "AST_PCT", "REB_PCT"]

    player_one = pairs[pairs["PLAYER_ID"] == 1].iloc[0]
    assert player_one["IS_BREAKOUT"]
    assert player_one["BREAKOUT_DIMENSIONS"] == 2
    assert player_one["BREAKOUT_PROFILE"] == "PTS_PER_36 + TS_PCT"


def test_add_following_season() -> None:
    """Test that a breakout receives the correct next-season values."""
    breakouts = pd.DataFrame({
        "PLAYER_ID": [1],
        "SEASON_START": [2021],
        "SEASON": ["2021-22"],
    })

    stats = pd.DataFrame({
        "PLAYER_ID": [1, 1],
        "SEASON_START": [2021, 2022],
        "SEASON": ["2021-22", "2022-23"],
        "TOTAL_MIN": [1000, 900],
        "MPG": [20.0, 22.0],
        "USG_PCT": [0.20, 0.22],
        "PTS_PER_36": [15.0, 14.0],
    })

    result = sa.add_following_season(
        breakouts,
        stats,
        ["PTS_PER_36"],
    )

    assert result.loc[0, "FOLLOW_UP_SEASON"] == "2022-23"
    assert result.loc[0, "FOLLOW_UP_TOTAL_MIN"] == 900
    assert result.loc[0, "FOLLOW_UP_PTS_PER_36"] == 14.0


def test_follow_up_filter() -> None:
    """Test that only follow-up seasons meeting the cutoff remain."""
    breakouts = pd.DataFrame({
        "PLAYER_ID": [1, 2, 3],
        "FOLLOW_UP_SEASON": ["2022-23", "2022-23", np.nan],
        "FOLLOW_UP_TOTAL_MIN": [500, 499, np.nan],
    })

    result = sa.filter_eligible_follow_ups(breakouts, 500)

    assert list(result["PLAYER_ID"]) == [1]


def test_retention_calculation() -> None:
    """Test the retention formula and nonqualifying metric handling."""
    breakouts = pd.DataFrame({
        "PREV_PTS_PER_36": [10.0],
        "PTS_PER_36": [15.0],
        "FOLLOW_UP_PTS_PER_36": [14.0],
        "QUALIFIED_PTS_PER_36": [True],
        "PREV_TS_PCT": [0.50],
        "TS_PCT": [0.60],
        "FOLLOW_UP_TS_PCT": [0.55],
        "QUALIFIED_TS_PCT": [False],
    })

    result = sa.calculate_retention(
        breakouts,
        ["PTS_PER_36", "TS_PCT"],
    )

    assert np.isclose(result.loc[0, "RETENTION_PTS_PER_36"], 0.80)
    assert pd.isna(result.loc[0, "RETENTION_TS_PCT"])


def test_sustainability_classification() -> None:
    """Test all three sustainability outcome labels."""
    breakouts = pd.DataFrame({
        "RETENTION_TEST": [1.20, 0.90, 0.50],
    })

    result = sa.classify_sustainability(
        breakouts,
        ["RETENTION_TEST"],
    )

    assert list(result["SUSTAINABILITY_RESULT"]) == [
        "Improved further",
        "Sustained at least 80%",
        "Regressed",
    ]


def test_characteristic_groups() -> None:
    """Test height conversion and career-stage grouping."""
    breakouts = pd.DataFrame({
        "HEIGHT": ["6-3"],
        "SEASON_START": [2022],
        "FROM_YEAR": [2020],
        "AGE": [22],
        "DRAFT_NUMBER": [10],
        "POSITION": ["G-F"],
    })

    result = sa.add_characteristic_groups(breakouts)

    assert result.loc[0, "HEIGHT_INCHES"] == 75
    assert result.loc[0, "EXPERIENCE"] == 2
    assert result.loc[0, "AGE_GROUP"] == "22 or younger"
    assert result.loc[0, "EXPERIENCE_GROUP"] == "0-2 years"
    assert result.loc[0, "DRAFT_GROUP"] == "Lottery"
    assert result.loc[0, "POSITION_GROUP"] == "Guard"


def main() -> None:
    """Run all project tests."""
    test_find_breakouts()
    test_add_following_season()
    test_follow_up_filter()
    test_retention_calculation()
    test_sustainability_classification()
    test_characteristic_groups()

    print("All project tests passed!")


if __name__ == "__main__":
    main()
