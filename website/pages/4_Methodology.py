"""Plain-language methods, sources, provenance, and limitations."""

import pandas as pd
import streamlit as st
from components.data_loader import METRICS, DATA_SOURCE_URL, FILES, baseline_numbers
from components.styles import page_header, resource_links

page_header("Methodology", "Make the definition inspectable.", "The analysis asks how much of a measured performance gain remains one season later. Every label follows the same explicit rules.")
numbers = baseline_numbers()
st.subheader("From season statistics to retained improvement")
steps = [
    ("01", "Load and merge", "Join traditional, advanced, and usage statistics by player ID and season."),
    ("02", "Pair consecutive seasons", "Keep adjacent years for the same player, then require at least 500 minutes in each."),
    ("03", "Measure and rank change", "Calculate changes in four metrics and rank each within the current season's eligible pairs."),
    ("04", "Identify a breakout", "Require at least two improvements at or above the 85th percentile."),
    ("05", "Attach the next season", "Require the immediately following season and at least 500 minutes to evaluate persistence."),
    ("06", "Measure retention", "Calculate retained improvement in each qualifying dimension, then take their unweighted mean."),
]
for number, title, detail in steps:
    st.markdown(f"**{number} · {title}**  \n{detail}")

st.subheader("Data and coverage")
st.write(f"The source is [Thomas Brescou's NBA Statistics Repository]({DATA_SOURCE_URL}). The included regular-season files span 1996–97 through 2022–23. The analysis first limits seasons to 2000–01 onward; consequently, identified breakouts run from {numbers['first_breakout']} to {numbers['last_breakout']}. The latest evaluable breakout season is {numbers['last_evaluated']}.")
st.write("Each supplied season file has one aggregate row per player-season, including players traded during a season. Team abbreviations do not identify separate team stints. Player characteristics are merged from the player index using PERSON_ID matched to PLAYER_ID; age comes from the advanced season file.")
st.write(f"The baseline contains {numbers['pairs']:,} eligible pairs and {numbers['breakouts']:,} detected breakouts. Of these, {numbers['any_follow_up']:,} have any next-season record, and {numbers['eligible']:,} meet the follow-up minute requirement. Counts describe seasons, not unique people.")

st.subheader("What counts toward a breakout?")
definitions = [
    ("Scoring", "Points per 36", "Points per game ÷ minutes per game × 36"),
    ("Efficiency", "True shooting %", "Shooting efficiency accounting for twos, threes, and free throws"),
    ("Playmaking", "Assist %", "Estimated share of teammates' field goals assisted while on court"),
    ("Rebounding", "Rebound %", "Estimated share of available rebounds collected while on court"),
]
st.dataframe(pd.DataFrame(definitions, columns=["Dimension", "Metric", "Meaning"]), hide_index=True, width="stretch")
st.write("Each change is ranked against other eligible player-season pairs in that same current season using pandas percentile ranks, with average ranks for ties. A rank of 0.85 qualifies. It is a relative improvement threshold, not an 85% increase in the statistic. MPG and USG% provide context but do not trigger breakouts or count toward average retention. Defense is excluded from the final four-dimension definition.")

st.subheader("How retention is calculated")
st.latex(r"R_m = \frac{x_{m,\mathrm{following}}-x_{m,\mathrm{previous}}}{x_{m,\mathrm{breakout}}-x_{m,\mathrm{previous}}}")
st.write("For example, a metric moving from 10 to 15 and then to 14 retains (14 − 10) / (15 − 10) = 80% of its improvement. This is a numerical illustration, not an observed player row.")
st.write("Only dimensions that qualified for the breakout contribute to the average. A mean above 100% is ‘Improved further’; 80–100%, including the boundaries, is ‘Sustained at least 80%’; below 80% is ‘Regressed.’ Negative retention means the metric fell below the pre-breakout level. Retention can exceed 100% and is not capped.")

st.subheader("Sensitivity and uncertainty")
st.write("The saved grid combines three minute cutoffs (500, 750, 1,000), three percentile thresholds (80th, 85th, 90th), and two minimum dimension counts (two or three). Each of the 18 definitions is evaluated at 70%, 80%, and 90% retention, for 54 specifications. The selected minute cutoff applies to all three seasons. These are precomputed results; the website does not rerun the research pipeline during interaction.")
st.write("The Findings page also includes the existing player-clustered bootstrap intervals: 2,000 resamples of whole players, using random seed 163. The 36.9–43.3% sensitivity range is a range across definitions, not a confidence interval. Overall stability does not show that every subgroup ranking survives the same changes.")

st.subheader("What the evidence cannot tell us")
for title, text in [
    ("Selection and dataset boundaries", "Missing or low-minute following seasons are not labeled as regressions. Results therefore describe qualifying returners. A missing record can reflect injury, retirement, leaving the league, or simply a follow-up outside the dataset; those causes are not identified here."),
    ("Threshold dependence", "Cutoffs alter the selected players and sample sizes. The grid tests specific alternatives; it does not prove that this definition is uniquely valid."),
    ("Retention ratios and averaging", "Small original gains can produce extreme retention ratios. Averaging allows a large retained gain in one dimension to offset a loss in another."),
    ("Regression to the mean", "Selecting unusually large observed gains can itself lead to lower subsequent performance. This descriptive analysis does not separate lasting skill change from random variation or provide a causal comparison group."),
    ("Unmeasured context", "Injuries, coaching, contracts, role changes, teammates, and team systems are not modeled. Age, experience, and performance profiles are associations, not causes or individual forecasts."),
    ("Coverage and player attributes", "The data end in 2022–23 and the trigger excludes defense. Height and weight come from a player index. Missing draft numbers are treated as undrafted, and draft-pick group labels are simplified historical categories."),
]:
    with st.expander(title):
        st.write(text)

st.subheader("Reproduce and inspect")
resource_links()
st.caption("The linked manuscript is the existing sensitivity-analysis draft. Its wording includes the broader 2000–01 study window; actual detected breakouts begin in 2001–02, as shown here. The website also makes the saved uncertainty intervals available.")
with st.expander("Where the displayed results come from"):
    st.dataframe(pd.DataFrame([{"Result": name.replace("_", " ").title(), "Saved file": f"code/{path}"} for name, path in FILES.items()]), hide_index=True, width="stretch")
    st.write("Player Explorer preserves saved eligible outcomes and joins raw following-season statistics for unevaluated breakouts. The headline eligible-pair count is a cached check of consecutive seasons and minute eligibility against the raw files. It does not rerank or rerun the breakout model.")

