"""Tests for publication-oriented robustness analyses."""

import numpy as np
import pandas as pd

import robustness_analysis as robustness


def test_attrition_summary() -> None:
    """Test that every detected breakout receives one attrition outcome."""
    all_breakouts = pd.DataFrame({
        "PLAYER_ID": [1, 2, 3, 4],
        "SEASON": ["2020-21"] * 4,
        "FOLLOW_UP_SEASON": ["2021-22", "2021-22", np.nan, "2021-22"],
        "FOLLOW_UP_TOTAL_MIN": [800, 200, np.nan, 900],
    })
    eligible = pd.DataFrame({
        "PLAYER_ID": [1, 4],
        "SEASON": ["2020-21", "2020-21"],
        "AVERAGE_RETENTION": [0.90, 0.50],
    })

    summary = robustness.create_attrition_summary(
        all_breakouts,
        eligible,
        minute_cutoff=500,
    )

    assert summary["COUNT"].sum() == 4
    assert set(summary["OUTCOME"]) == {
        "Eligible follow-up: sustained or improved",
        "Eligible follow-up: regressed",
        "Following season below 500 minutes",
        "No following-season record",
    }


def test_repeat_player_summary() -> None:
    """Test repeated-player counts in two analysis samples."""
    all_breakouts = pd.DataFrame({"PLAYER_ID": [1, 1, 2, 3]})
    eligible = pd.DataFrame({"PLAYER_ID": [1, 2, 3]})

    summary = robustness.summarize_repeat_players(
        all_breakouts,
        eligible,
    )

    assert summary.loc[0, "BREAKOUT_SEASONS"] == 4
    assert summary.loc[0, "UNIQUE_PLAYERS"] == 3
    assert summary.loc[0, "PLAYERS_WITH_MULTIPLE_BREAKOUTS"] == 1
    assert summary.loc[1, "PLAYERS_WITH_MULTIPLE_BREAKOUTS"] == 0


def test_cluster_bootstrap_is_reproducible() -> None:
    """Test that a fixed seed produces identical confidence intervals."""
    data = pd.DataFrame({
        "PLAYER_ID": [1, 1, 2, 3, 3],
        "SUSTAINED": [True, False, True, False, False],
    })

    first = robustness.player_cluster_bootstrap_ci(
        data,
        "SUSTAINED",
        samples=200,
        seed=10,
    )
    second = robustness.player_cluster_bootstrap_ci(
        data,
        "SUSTAINED",
        samples=200,
        seed=10,
    )

    assert first == second
    assert np.isclose(first[0], 0.40)
    assert first[1] <= first[0] <= first[2]


def test_alternative_outcome() -> None:
    """Test direct follow-up minus breakout change calculations."""
    breakouts = pd.DataFrame({
        "QUALIFIED_TEST": [True, True, False],
        "TEST": [10.0, 12.0, 20.0],
        "FOLLOW_UP_TEST": [11.0, 10.0, 25.0],
    })

    summary = robustness.summarize_alternative_outcome(
        breakouts,
        ["TEST"],
    )

    assert summary.loc[0, "COUNT"] == 2
    assert np.isclose(
        summary.loc[0, "MEDIAN_FOLLOW_UP_MINUS_BREAKOUT"],
        -0.5,
    )
    assert np.isclose(
        summary.loc[0, "PERCENT_MAINTAINED_OR_IMPROVED"],
        50.0,
    )


def main() -> None:
    """Run all robustness-analysis tests."""
    test_attrition_summary()
    test_repeat_player_summary()
    test_cluster_bootstrap_is_reproducible()
    test_alternative_outcome()
    print("All robustness tests passed!")


if __name__ == "__main__":
    main()
