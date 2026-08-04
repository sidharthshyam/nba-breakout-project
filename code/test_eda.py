import pandas as pd
from eda import filter_seasons, draft_group, create_merged_dataset


def test_filter_seasons():
    test = pd.DataFrame({
        "SEASON": ["1998-99", "1999-00", "2020-21"]
    })

    result = filter_seasons(test, 1999)

    assert len(result) == 2
    print("filter_seasons passed")


def test_draft_group():
    assert draft_group(3) == "Top 5"
    assert draft_group(10) == "Lottery"
    assert draft_group(25) == "1st Round"
    assert draft_group(45) == "2nd Round"

    print("draft_group passed")


def test_create_merged_dataset():
    traditional = pd.DataFrame({
        "PLAYER_ID": [1],
        "PLAYER_NAME": ["Player A"],
        "SEASON": ["2023-24"],
        "MIN": [36],
        "PTS": [18]
    })

    advanced = pd.DataFrame({
        "PLAYER_ID": [1],
        "SEASON": ["2023-24"],
        "AGE": [22],
        "USG_PCT": [22],
        "TS_PCT": [0.60],
        "AST_PCT": [18],
        "REB_PCT": [10],
        "DEF_RATING": [110],
        "PIE": [0.12]
    })

    player_info = pd.DataFrame({
        "PERSON_ID": [1],
        "POSITION": ["G"],
        "HEIGHT": ["6-3"],
        "WEIGHT": [190],
        "DRAFT_YEAR": [2022],
        "DRAFT_ROUND": [1],
        "DRAFT_NUMBER": [12],
        "FROM_YEAR": [2023]
    })

    merged = create_merged_dataset(
        traditional,
        advanced,
        player_info
    )

    assert len(merged) == 1
    assert "PTS_PER_36" in merged.columns
    assert merged["PTS_PER_36"].values[0] == 18

    print("create_merged_dataset passed")


def main():
    test_filter_seasons()
    test_draft_group()
    test_create_merged_dataset()

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()
