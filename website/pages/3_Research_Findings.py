"""Interactive figures for the three research questions."""

import streamlit as st
from components.data_loader import baseline_numbers, load_table
from components.charts import outcome_chart, dimension_chart, profile_chart, group_chart
from components.styles import page_header, show_chart, takeaway

page_header("Findings & Data", "What survives the breakout?", "Three questions about persistence, the type of improvement, and the players behind it. All results here use the baseline definition.")
numbers = baseline_numbers()
rq1, rq2, rq3 = st.tabs(["01 · Following-season outcomes", "02 · Performance dimensions", "03 · Player characteristics"])

with rq1:
    st.subheader("How often does improvement last?")
    st.metric("Median overall improvement retained", f"{numbers['median_retention']:.1%}")
    show_chart(outcome_chart(load_table("outcomes")), "rq1_outcomes")
    outcomes = load_table("outcomes")[["RESULT", "COUNT", "PERCENT"]].copy()
    outcomes.columns = ["Following-season outcome", "Player-seasons", "Share (%)"]
    st.dataframe(outcomes.round(1), hide_index=True, width="stretch")
    takeaway("Sustainability is a matter of degree. Retaining 70% of a large gain can still leave a player well above the pre-breakout level, even though this study labels it regression.")
    intervals = load_table("intervals")
    overall = intervals[intervals.VARIABLE == "Overall"].iloc[0]
    st.write(f"The overall rate is {overall.RATE:.1f}%, with a saved player-clustered 95% bootstrap interval of {overall.CI_LOWER:.1f}%–{overall.CI_UPPER:.1f}%. Resampling whole players accounts for players who contribute multiple breakout seasons.")
    st.caption("The bootstrap used 2,000 resamples and a fixed random seed. This interval describes sampling uncertainty under the resampling assumptions; it does not remove selection bias or measurement limitations.")
    with st.expander("Where did the other detected breakouts go?"):
        attrition = load_table("attrition").rename(columns={"OUTCOME": "Follow-up status", "COUNT": "Player-seasons", "PERCENT_OF_ALL_BREAKOUTS": "Share of all detected (%)"})
        st.dataframe(attrition.round(1), hide_index=True, width="stretch")
        st.caption("Missing and low-minute follow-ups are excluded from the sustainability denominator. Missing records also include the dataset's final season, whose next season is outside coverage.")

with rq2:
    st.subheader("Which kinds of improvement persist?")
    show_chart(dimension_chart(load_table("dimensions")), "rq2_dimensions")
    st.write("Scoring and playmaking have the highest median retention in this sample. None of the four dimensions reaches 80% at the median. These dimension-level estimates use only the breakouts that qualified in that dimension.")
    st.subheader("Combinations of improvements")
    profiles = load_table("profiles")
    minimum = st.slider("Minimum observations in a profile", min_value=10, max_value=100, value=10, step=5)
    visible = profiles[profiles.COUNT >= minimum]
    show_chart(profile_chart(visible), "rq2_profiles")
    st.caption("Each bar shows the overall average-retention outcome for that profile. The original summary includes profiles with at least 10 observations. Hover for sample size and median retention.")
    if (visible.COUNT < 30).any():
        st.warning("Some displayed profiles have fewer than 30 observations. Treat their rankings as exploratory; 30 is a display caution, not a formal reliability cutoff.")
    st.write("Scoring plus playmaking plus rebounding has the highest observed sustainability rate among the saved profiles, but its sample is small. The larger scoring-plus-playmaking group also performs relatively well. These descriptive rankings do not establish statistical differences between profiles.")
    show_chart(group_chart(load_table("dimension_counts"), "BREAKOUT_DIMENSIONS", "Does broader improvement last longer?", [2, 3, 4]), "rq2_counts")
    takeaway("More qualifying dimensions did not automatically mean more persistence. The observed rate is lower for three- and four-dimensional breakouts than for two-dimensional breakouts; the four-dimensional group contains only 14 seasons.")

with rq3:
    st.subheader("How does career stage relate to persistence?")
    intervals = load_table("intervals")
    summaries = [
        ("age", "AGE_GROUP", "Sustainability by age", ["22 or younger", "23-25", "26-28", "29 or older"]),
        ("experience", "EXPERIENCE_GROUP", "Sustainability by prior NBA experience", ["0-2 years", "3-5 years", "6+ years"]),
        ("position", "POSITION_GROUP", "Sustainability by primary position", ["Guard", "Forward", "Center"]),
        ("draft", "DRAFT_GROUP", "Sustainability by draft group", ["Lottery", "Rest of first round", "Second round", "Undrafted"]),
    ]
    for name, group, title, order in summaries:
        show_chart(group_chart(load_table(name), group, title, order, intervals), f"rq3_{name}")
        st.caption("Bars show observed rates; error bars show saved player-clustered 95% bootstrap intervals. Hover to see the group sample size and median retention.")
    takeaway("Younger and less experienced players show higher sustainability rates. Age and experience overlap as measures of career stage, so these are associations rather than independent causal effects.")
    st.write("Position and draft-group differences are much smaller, and their uncertainty intervals overlap substantially. These summaries are not adjusted for injuries, role, era, or other differences between players.")
    with st.expander("Height and weight by outcome"):
        physical = load_table("physical").rename(columns={"SUSTAINABILITY_RESULT": "Outcome", "COUNT": "Player-seasons", "HEIGHT_INCHES": "Median height (in)", "WEIGHT": "Median weight (lb)"})
        st.dataframe(physical, hide_index=True, width="stretch")
        st.caption("Similar group medians do not establish that height or weight has no relationship with sustainability. Player-index measurements may not describe a player's size in the specific breakout season.")

