"""Interactive access to the precomputed robustness grid."""

import streamlit as st
from components.data_loader import BASELINE, load_table, select_specification
from components.charts import sensitivity_chart, sensitivity_heatmap
from components.styles import page_header, show_chart, takeaway

page_header("Definition Lab", "What counts as a breakout?", "Change the assumptions and see how the answer moves. All 54 combinations below come from the saved sensitivity analysis.")
data = load_table("sensitivity")
baseline = select_specification(data, *BASELINE)
with st.container(border=True):
    a, b, c, d = st.columns(4)
    minutes = a.selectbox("Minimum minutes", [500, 750, 1000], key="lab_minutes")
    percentile = b.selectbox("Breakout percentile", [.80, .85, .90], index=1, format_func=lambda x: f"{x:.0%}", key="lab_percentile")
    dimensions = c.selectbox("Minimum dimensions", [2, 3], key="lab_dimensions")
    retention = d.selectbox("Improvement retained", [.70, .80, .90], index=1, format_func=lambda x: f"{x:.0%}", key="lab_retention")
    st.caption("The minute cutoff applies to the previous, breakout, and following seasons. Percentiles are recalculated among the eligible pairs for each definition.")
selected = select_specification(data, minutes, percentile, dimensions, retention)
cols = st.columns(4)
cols[0].metric("Detected breakouts", f"{int(selected.BREAKOUTS_FOUND):,}")
cols[1].metric("Eligible follow-ups", f"{int(selected.ELIGIBLE_FOLLOW_UPS):,}")
cols[2].metric("Sustained or improved", f"{int(selected.SUSTAINED_COUNT):,}")
cols[3].metric("Sustainability rate", f"{selected.SUSTAINABILITY_RATE:.1f}%",
               delta=f"{selected.SUSTAINABILITY_RATE - baseline.SUSTAINABILITY_RATE:+.1f} pp vs baseline", delta_color="off")
st.caption(f"{int(selected.BREAKOUTS_WITH_ANY_FOLLOW_UP):,} have any following-season record; {int(selected.ELIGIBLE_FOLLOW_UPS):,} meet its minute requirement. Baseline comparison: 500 minutes · 85th percentile · ≥2 dimensions · 80% retention ({baseline.SUSTAINABILITY_RATE:.1f}%).")
st.write(f"At this setting, **{int(selected.SUSTAINED_COUNT):,}** eligible breakouts retained at least **{retention:.0%}** of their original improvement; **{int(selected.ELIGIBLE_FOLLOW_UPS - selected.SUSTAINED_COUNT):,}** fell below that standard.")
st.caption("The sensitivity table stores combined sustained-or-improved outcomes, not a separate improved-further count for every setting.")

show_chart(sensitivity_heatmap(data, selected), "sensitivity_heatmap")
st.caption(f"Hold ≥{dimensions} dimensions and {retention:.0%} retention constant. Each cell compares a minute cutoff and breakout percentile; hover for the exact rate. Colors share a fixed 0–100% scale.")
show_chart(sensitivity_chart(data, selected), "sensitivity_comparison")
st.caption("Brick red marks your selected breakout definition. The dotted line marks 50%; the horizontal axis starts at zero. P80/P85/P90 mean the improvement percentile cutoffs.")
primary = data[(data.RETENTION_THRESHOLD - .8).abs() < 1e-8]
takeaway(f"At the primary 80% retention standard, sustainability ranges from {primary.SUSTAINABILITY_RATE.min():.1f}% to {primary.SUSTAINABILITY_RATE.max():.1f}% across all 18 breakout definitions. None classifies a majority as sustained.")
st.write(f"The number of detected breakouts ranges from {int(primary.BREAKOUTS_FOUND.min()):,} to {int(primary.BREAKOUTS_FOUND.max()):,}. The precise set of breakouts is sensitive to the definition, even though the overall sustainability rate varies less. This check supports the main overall finding; it does not establish a uniquely correct definition or confirm every age-group or profile ranking under every setting.")
st.write("Changing the retention standard changes what success means. The conclusion about fewer than half applies across the tested definitions at 80%; it should not automatically be extended to the more lenient 70% standard.")
st.download_button("Download the full sensitivity grid", data.to_csv(index=False), file_name="nba_breakout_sensitivity.csv", mime="text/csv")

