"""Editorial abstract and entry point to the research."""

import streamlit as st
from components.data_loader import baseline_numbers, load_table
from components.charts import outcome_chart
from components.styles import show_chart, takeaway

numbers = baseline_numbers()
st.markdown(f'''<section class="hero">
  <div>
    <div class="section-label">Research abstract</div>
    <h1 class="hero-title">NBA Breakout Lab</h1>
    <p class="hero-question">Which NBA breakout seasons were built to last?</p>
    <p class="hero-deck">An independent study of how much player improvement remains one season later,
    with interactive access to the underlying player seasons and definition choices.</p>
  </div>
  <div class="hero-result">
    <div class="data-label">Principal finding</div>
    <span class="hero-figure">{numbers['rate']:.1f}%</span>
    <p>{numbers['successes']:,} of {numbers['eligible']:,} eligible breakout seasons retained
    at least 80% of their improvement or improved further.</p>
  </div>
</section>''', unsafe_allow_html=True)

st.markdown(f'''<div class="data-strip" aria-label="Study sample sizes">
  <div class="data-item"><span class="data-label">Consecutive pairs</span><span class="data-value">{numbers['pairs']:,}</span></div>
  <div class="data-item"><span class="data-label">Detected breakouts</span><span class="data-value">{numbers['breakouts']:,}</span></div>
  <div class="data-item"><span class="data-label">Any follow-up</span><span class="data-value">{numbers['any_follow_up']:,}</span></div>
  <div class="data-item"><span class="data-label">Eligible follow-ups</span><span class="data-value">{numbers['eligible']:,}</span></div>
</div>''', unsafe_allow_html=True)

abstract, method = st.columns([1.45, 1], gap="large")
with abstract:
    st.markdown('''<section class="essay-panel"><div class="section-label">Abstract</div>
    <h2>What remains after the leap?</h2>
    <p>Basketball fans notice when a player makes a sudden leap. This study follows those
    player seasons into the next year. It asks how often the original improvement lasts,
    which kinds of gains persist, and how sustainability varies across player characteristics.</p>
    <p>Most eligible breakouts retained less than 80% of their measured gain. That label
    does not mean the player necessarily fell below their pre-breakout level.</p></section>''',
                unsafe_allow_html=True)
with method:
    st.markdown('''<section class="essay-panel"><div class="section-label">Method in brief</div>
    <h2>A measurable definition</h2>
    <p>A breakout requires at least 500 minutes in consecutive seasons and gains at or
    above the 85th percentile in at least two of four dimensions: scoring, efficiency,
    playmaking, and rebounding. Retention compares the following season with the
    pre-breakout season.</p></section>''', unsafe_allow_html=True)
    st.page_link("pages/4_Methodology.py", label="Read the full methodology →")

st.subheader("Following-season outcomes")
chart, interpretation = st.columns([1.5, .85], gap="large")
with chart:
    show_chart(outcome_chart(load_table("outcomes")), "home_outcomes")
with interpretation:
    st.markdown('<div class="section-label">Interpretation</div>', unsafe_allow_html=True)
    st.write("The outcomes describe the 660 breakouts with a qualifying following season. Players without an eligible follow-up are excluded from these percentages.")
    takeaway("A breakout can partly fade and still represent meaningful progress over the season before it.")

st.subheader("Explore the evidence")
st.write("The underlying observations and alternative thresholds are available for inspection.")
st.page_link("pages/1_Player_Explorer.py", label="Player Explorer — compare three seasons and the qualifying dimensions →")
st.page_link("pages/2_Definition_Lab.py", label="Definition Lab — test the 54 saved specifications →")
st.page_link("pages/3_Research_Findings.py", label="Findings & Data — read the three research questions →")
st.page_link("pages/6_Publications.py", label="Publications — inspect the manuscript, data source, and code →")

st.caption(f"Detected breakout seasons: {numbers['first_breakout']}–{numbers['last_breakout']}; evaluated breakouts through {numbers['last_evaluated']}. Counts describe player-seasons, so one player may appear more than once.")
