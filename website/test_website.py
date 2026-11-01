"""Run with python -m unittest discover -s website -p 'test_website.py' -v."""

from itertools import product
from pathlib import Path
import math
import sys
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from components.data_loader import (
    BASELINE, FILES, METRICS, SENSITIVITY_KEYS, WEBSITE_DIR,
    baseline_numbers, dimension_table, filter_players, format_metric,
    load_explorer, load_season_stats, load_table, select_specification,
    player_interpretation, sustained_count,
)


class DataIntegrityTests(unittest.TestCase):
    """Check denominators, joins, saved summaries, and numerical interpretation."""

    def test_required_files_and_baseline(self) -> None:
        for name in FILES:
            self.assertFalse(load_table(name).empty, name)
        numbers = baseline_numbers()
        self.assertEqual([numbers[c] for c in ["pairs", "breakouts", "any_follow_up", "eligible", "successes"]],
                         [6002, 808, 739, 660, 273])
        self.assertAlmostEqual(numbers["rate"], 273 / 660 * 100)
        self.assertEqual(numbers["first_breakout"], "2001-02")
        self.assertEqual(numbers["last_evaluated"], "2021-22")

    def test_all_sensitivity_settings_and_units(self) -> None:
        data = load_table("sensitivity")
        self.assertEqual(len(data), 54)
        self.assertFalse(data.duplicated(SENSITIVITY_KEYS).any())
        self.assertTrue(data.SUSTAINABILITY_RATE.between(0, 100).all())
        self.assertTrue((data.ELIGIBLE_FOLLOW_UPS <= data.BREAKOUTS_WITH_ANY_FOLLOW_UP).all())
        self.assertTrue((data.BREAKOUTS_WITH_ANY_FOLLOW_UP <= data.BREAKOUTS_FOUND).all())
        for settings in product([500, 750, 1000], [.8, .85, .9], [2, 3], [.7, .8, .9]):
            row = select_specification(data, *settings)
            self.assertAlmostEqual(row.SUSTAINABILITY_RATE, row.SUSTAINED_COUNT / row.ELIGIBLE_FOLLOW_UPS * 100)
        primary = data[data.RETENTION_THRESHOLD == .8]
        self.assertAlmostEqual(round(primary.SUSTAINABILITY_RATE.min(), 1), 36.9)
        self.assertAlmostEqual(round(primary.SUSTAINABILITY_RATE.max(), 1), 43.3)
        with self.assertRaises(ValueError):
            select_specification(data, 499, .85, 2, .8)
        with self.assertRaises(ValueError):
            sustained_count(pd.Series({"SUSTAINABILITY_RATE": 41.4, "ELIGIBLE_FOLLOW_UPS": 660}))

    def test_outcomes_and_retention_match_individual_rows(self) -> None:
        data = load_table("eligible")
        self.assertFalse(data.duplicated(["PLAYER_ID", "SEASON"]).any())
        self.assertTrue((data.FOLLOW_UP_TOTAL_MIN >= 500).all())
        self.assertTrue(data.FOLLOW_UP_SEASON.notna().all())
        next_year = data.FOLLOW_UP_SEASON.str[:4].astype(int)
        self.assertTrue((next_year - data.SEASON_START == 1).all())
        summary = load_table("outcomes")
        counts = data.SUSTAINABILITY_RESULT.value_counts()
        for _, row in summary.iterrows():
            self.assertEqual(row.COUNT, counts[row.RESULT])
            self.assertAlmostEqual(row.PERCENT, row.COUNT / len(data) * 100)
        for metric in METRICS:
            qualified = data[f"QUALIFIED_{metric}"]
            expected = ((data[f"FOLLOW_UP_{metric}"] - data[f"PREV_{metric}"])
                        / (data[metric] - data[f"PREV_{metric}"]))
            for actual, calculated in zip(data.loc[qualified, f"RETENTION_{metric}"], expected[qualified]):
                self.assertTrue(math.isclose(actual, calculated, abs_tol=1e-9))
            self.assertTrue(data.loc[~qualified, f"RETENTION_{metric}"].isna().all())
        calculated_average = data[[f"RETENTION_{m}" for m in METRICS]].mean(axis=1)
        self.assertTrue(((data.AVERAGE_RETENTION - calculated_average).abs() < 1e-9).all())

    def test_group_tables_reconcile(self) -> None:
        data = load_table("eligible")
        groups = [("profiles", "BREAKOUT_PROFILE"), ("dimension_counts", "BREAKOUT_DIMENSIONS"),
                  ("age", "AGE_GROUP"), ("experience", "EXPERIENCE_GROUP"),
                  ("position", "POSITION_GROUP"), ("draft", "DRAFT_GROUP")]
        for name, column in groups:
            for _, row in load_table(name).iterrows():
                group = data[data[column] == row[column]]
                self.assertEqual(row.COUNT, len(group))
                self.assertAlmostEqual(row.MEDIAN_RETENTION, group.AVERAGE_RETENTION.median())
                self.assertAlmostEqual(row.SUSTAINABILITY_RATE, (group.AVERAGE_RETENTION >= .8).mean() * 100)
        for _, row in load_table("dimensions").iterrows():
            selected = data[data[f"QUALIFIED_{row.DIMENSION}"]]
            retained = selected[f"RETENTION_{row.DIMENSION}"]
            self.assertEqual(row.COUNT, len(selected))
            self.assertAlmostEqual(row.MEDIAN_RETENTION, retained.median())
            self.assertAlmostEqual(row.PERCENT_SUSTAINED, (retained >= .8).mean() * 100)

    def test_explorer_keeps_unassessed_rows_and_correct_joins(self) -> None:
        data = load_explorer()
        self.assertEqual(len(data), 808)
        self.assertFalse(data.duplicated(["PLAYER_ID", "SEASON"]).any())
        self.assertEqual(int(data.EVALUATED.sum()), 660)
        self.assertEqual(int(data.FOLLOW_UP_SEASON.notna().sum()), 739)
        self.assertTrue((data.loc[~data.EVALUATED, "SUSTAINABILITY_RESULT"] == "Not evaluated").all())
        stats = load_season_stats().set_index(["PLAYER_ID", "SEASON"])
        for _, row in data[data.FOLLOW_UP_SEASON.notna()].iterrows():
            follow = stats.loc[(row.PLAYER_ID, row.FOLLOW_UP_SEASON)]
            self.assertAlmostEqual(row.FOLLOW_UP_PTS_PER_36, follow.PTS_PER_36)
        missing = data[data.FOLLOW_UP_SEASON.isna()]
        self.assertTrue(missing.FOLLOW_UP_PTS_PER_36.isna().all())

    def test_filters_and_missing_optional_fields(self) -> None:
        data = load_explorer()
        row = data.iloc[0]
        selected = filter_players(data, [row.SEASON], [row.SUSTAINABILITY_RESULT],
                                  [row.PROFILE_LABEL], [row.BREAKOUT_DIMENSIONS])
        self.assertIn(row.PLAYER_ID, selected.PLAYER_ID.to_list())
        self.assertTrue(filter_players(data, ["1900-01"]).empty)
        partial = row.drop(labels=[c for c in row.index if c.startswith("FOLLOW_UP_") or c.startswith("RETENTION_")])
        table = dimension_table(partial)
        self.assertEqual(len(table), 4)
        self.assertEqual(set(table.Following), {"Unavailable"})
        self.assertEqual(format_metric(.573, "TS_PCT"), "57.3%")
        self.assertEqual(format_metric(.05, "TS_PCT", True), "+5.0 pp")
        unavailable = data[~data.EVALUATED].iloc[0]
        self.assertIn("not evaluated", player_interpretation(unavailable))

    def test_loaders_allow_missing_optional_context(self) -> None:
        """Missing context in input files must not prevent the explorer loading."""
        original_read_csv = pd.read_csv

        def read_without_usage(*args, **kwargs):
            return original_read_csv(*args, **kwargs).drop(columns="USG_PCT", errors="ignore")

        with patch("components.data_loader.pd.read_csv", side_effect=read_without_usage):
            stats = load_season_stats.__wrapped__()
        self.assertTrue(stats.USG_PCT.isna().all())

        def read_without_context(name):
            return load_table(name).drop(columns=["FOLLOW_UP_MPG", "FOLLOW_UP_USG_PCT"], errors="ignore")

        with patch("components.data_loader.load_table", side_effect=read_without_context), \
                patch("components.data_loader.load_season_stats", return_value=stats):
            data = load_explorer.__wrapped__()
        self.assertEqual(len(data), 808)
        self.assertTrue(data.FOLLOW_UP_USG_PCT.isna().all())
        self.assertTrue(data.loc[data.EVALUATED, "FOLLOW_UP_MPG"].notna().all())


class WebsiteInteractionTests(unittest.TestCase):
    """Exercise real Streamlit pages and input changes without a browser server."""

    def app(self) -> AppTest:
        return AppTest.from_file(str(WEBSITE_DIR / "app.py"), default_timeout=30).run()

    def assert_page_ok(self, app: AppTest) -> None:
        self.assertFalse(list(app.exception), [e.message for e in app.exception])
        self.assertFalse(list(app.error), [e.value for e in app.error])

    def test_all_pages_render(self) -> None:
        app = self.app()
        self.assert_page_ok(app)
        home_text = " ".join(item.value for item in app.markdown)
        for figure in ["6,002", "808", "660", "41.4%"]:
            self.assertIn(figure, home_text)
        for filename in ["1_Player_Explorer", "2_Definition_Lab", "3_Research_Findings", "4_Methodology", "5_About", "6_Publications"]:
            app.switch_page(f"pages/{filename}.py").run()
            self.assert_page_ok(app)

    def test_definition_controls_change_results(self) -> None:
        app = self.app().switch_page("pages/2_Definition_Lab.py").run()
        app.selectbox(key="lab_minutes").set_value(1000)
        app.selectbox(key="lab_percentile").set_value(.9)
        app.selectbox(key="lab_dimensions").set_value(3)
        app.selectbox(key="lab_retention").set_value(.9)
        app.run()
        self.assert_page_ok(app)
        self.assertEqual([m.value for m in app.metric], ["47", "35", "11", "31.4%"])
        self.assertIn("-9.9 pp", app.metric[3].delta)

    def test_player_switch_empty_and_unassessed(self) -> None:
        app = self.app().switch_page("pages/1_Player_Explorer.py").run()
        app.multiselect(key="filter_outcomes").set_value(["Not evaluated"]).run()
        self.assert_page_ok(app)
        self.assertEqual(app.metric[0].value, "Not evaluated")
        self.assertEqual(app.metric[1].value, "Not evaluated")
        app.multiselect(key="filter_outcomes").set_value(["Improved further"])
        app.multiselect(key="filter_seasons").set_value(["2022-23"]).run()
        self.assert_page_ok(app)
        self.assertTrue(any("No breakout seasons match" in item.value for item in app.info))

    def test_optional_context_columns_are_absent(self) -> None:
        data = load_explorer().drop(columns=["MPG", "PREV_MPG", "FOLLOW_UP_MPG", "DELTA_MPG", "USG_PCT", "PREV_USG_PCT", "FOLLOW_UP_USG_PCT", "DELTA_USG_PCT"])
        with patch("components.data_loader.load_explorer", return_value=data):
            app = self.app().switch_page("pages/1_Player_Explorer.py").run()
            self.assert_page_ok(app)


if __name__ == "__main__":
    unittest.main(verbosity=2)
