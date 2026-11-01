# Website data audit

The website uses existing research outputs, with a small read-only merge of raw
season statistics for coverage and unevaluated follow-ups. No research output was
regenerated or overwritten while building the website.

## Verified baseline

| Quantity | Verified value | Source |
| --- | ---: | --- |
| Eligible consecutive-season pairs | 6,002 | Raw season tables, same year/minute rules as ba.py |
| Detected breakout player-seasons | 808 | nba_breakout_seasons.csv |
| Any following-season record | 739 | Sensitivity baseline, reconciled to raw follow-up joins |
| Eligible following season | 660 | nba_breakout_sustainability.csv |
| Sustained or improved | 273 (41.3636%) | Individual average retention >= 0.80 |
| Regressed | 387 (58.6364%) | sustainability_summary.csv and individual rows |
| Sustained 80–100% | 101 (15.3030%) | Same |
| Improved further | 172 (26.0606%) | Same |
| Sensitivity range at 80% retention | 36.9231–43.2815% | 18 definitions from the saved sensitivity grid |

All three raw season tables have unique PLAYER_ID/SEASON keys, as do both
breakout result files. The player index has unique PERSON_ID values.

## Clarifications and discrepancies

1. The manuscript describes the study window as 2000–01 onward, and one sentence
   also uses that as the breakout window. Actual detected breakouts start in
   **2001–02**, because 2000–01 is needed as the prior season. The website reports
   the actual range. Eligible follow-ups evaluate breakouts through 2021–22.
2. The 148 unevaluated breakouts include 79 with a following season below 500
   minutes and 69 without a following-season record. Of the 69, 38 are 2022–23
   breakouts whose follow-up is outside the dataset, while 31 are earlier cases.
   None is relabeled as regression by the website.
3. The sensitivity file contains full-precision combined sustainability rates
   and eligible counts, not all three outcome categories for each specification.
   The website recovers the integer sustained count only after verifying that
   rate × sample size / 100 is within 1e-6 of an integer. It does not invent an
   improved-further count.
4. The exported breakout-only CSV lacks qualification flags and profile strings.
   For the Explorer, those are reconstructed from its saved percentile values
   and the baseline 0.85 cutoff. Saved eligible outcomes remain authoritative.
5. Summary rates and sensitivity rates are already percentages (0–100), whereas
   retention, percentiles, TS%, AST%, REB%, and USG% are stored as proportions.
   Retention can be negative or greater than one. Rate changes are displayed in
   percentage points; they are not relative percent changes.
6. The sensitivity grid tests the overall result. It does not establish the
   robustness of every age-group, dimension, or profile ranking.
7. The manuscript is provided unchanged as a Word download. The site adds the
   saved bootstrap intervals from robustness_outputs; it does not claim that the
   manuscript has been peer reviewed or professionally endorsed.

## Verification

Run `python -m unittest discover -s website -p 'test_website.py' -v` from the
repository root. Tests reconcile saved summaries to individual rows, evaluate
all 54 sensitivity selections, check follow-up joins and retention formulas,
and exercise the Streamlit pages, controls, and empty/missing-data cases.

Completed local verification on October 7, 2026:

- All 11 website tests passed, including missing optional context in input files.
- Existing test_project.py, test_eda.py, and test_robustness.py passed unchanged.
- All six pages were inspected in the local browser. Phone-width checks at
  390 pixels covered navigation, text wrapping, charts, controls, and the
  retention formula; wide tables remain horizontally scrollable.
- The sensitivity CSV download completed successfully. Chart category ordering,
  percent formatting, and annotation placement were checked against saved data.
- No research CSVs were regenerated and no public deployment was performed.
