"""Inspect baseline breakout seasons, including those without eligible follow-ups."""

import pandas as pd
import streamlit as st
from components.data_loader import (METRICS, OUTCOMES, load_explorer, filter_players,
                                    dimension_table, player_interpretation, format_metric)
from components.charts import player_chart
from components.styles import page_header, show_chart, takeaway

page_header("Player Explorer", "Every breakout has a next chapter.",
            "Search the baseline breakout list and compare three seasons of performance. This explorer uses the 500-minute, 85th-percentile, two-dimension definition.")
data = load_explorer()
with st.expander("Filter the breakout list", expanded=False):
    a, b = st.columns(2)
    seasons = a.multiselect("Breakout season", sorted(data.SEASON.unique(), reverse=True), key="filter_seasons")
    outcomes = b.multiselect("Following-season outcome", OUTCOMES + ["Not evaluated"], key="filter_outcomes")
    profiles = a.multiselect("Breakout profile", sorted(data.PROFILE_LABEL.unique()), key="filter_profiles")
    dimensions = b.multiselect("Qualifying dimensions", sorted(data.BREAKOUT_DIMENSIONS.unique()), key="filter_dimensions")
    st.caption("Leave a filter empty to include all values. Filters apply before player selection.")
filtered = filter_players(data, seasons, outcomes, profiles, dimensions)
st.caption(f"{len(filtered):,} matching player-seasons · {filtered.PLAYER_ID.nunique():,} players")
if filtered.empty:
    st.info("No breakout seasons match this combination. Clear one or more filters above to explore again.")
    st.stop()

names = filtered.groupby("PLAYER_ID")["PLAYER_NAME"].first().to_dict()
ids = sorted(names, key=names.get)
default_id = next((pid for pid in ids if names[pid] == "Giannis Antetokounmpo"), ids[0])
a, b = st.columns([2, 1])
player_id = a.selectbox("Search for a player", ids, index=ids.index(default_id), format_func=names.get, key="player_id")
player = filtered[filtered.PLAYER_ID == player_id]
season = b.selectbox("Select a breakout season", sorted(player.SEASON, reverse=True), key="player_season")
row = player[player.SEASON == season].iloc[0]
st.subheader(f"{row.PLAYER_NAME} · {season}")
st.write(row.PROFILE_LABEL)
cols = st.columns(3)
cols[0].metric("Following-season outcome", row.SUSTAINABILITY_RESULT)
cols[1].metric("Average retention", f"{row.AVERAGE_RETENTION:.1%}" if row.EVALUATED else "Not evaluated")
cols[2].metric("Qualifying dimensions", int(row.BREAKOUT_DIMENSIONS))
takeaway(player_interpretation(row))
if not row.EVALUATED:
    st.info(f"{row.FOLLOW_UP_STATUS}. Available season statistics are shown for context; this observation is excluded from sustainability rates.")
st.caption(f"Previous: {row.PREV_SEASON} → Breakout: {row.SEASON} → Following: {row.FOLLOW_UP_SEASON if pd.notna(row.FOLLOW_UP_SEASON) else 'unavailable'}")

tabs = st.tabs([v[0] for v in METRICS.values()])
for tab, metric in zip(tabs, METRICS):
    with tab:
        show_chart(player_chart(row, metric), f"player_{metric}")
        qualified = row[f"QUALIFIED_{metric}"]
        st.caption(f"{METRICS[metric][1]} {'qualified' if qualified else 'did not qualify'} at the 85th-percentile cutoff. A missing following-season point is not treated as zero.")

st.subheader("The numbers behind the label")
st.dataframe(dimension_table(row), hide_index=True, width="stretch")
st.caption("Percentage-point changes (pp) are differences between rates. Retention is evaluated only for qualifying dimensions with an eligible follow-up. The overall retention is their unweighted mean; one dimension can offset another.")
with st.expander("Playing time and offensive role · context only"):
    context = []
    for metric, label in [("MPG", "Minutes per game"), ("USG_PCT", "Usage rate")]:
        context.append({"Context": label,
                        "Previous": format_metric(row.get(f"PREV_{metric}"), metric),
                        "Breakout": format_metric(row.get(metric), metric),
                        "Following": format_metric(row.get(f"FOLLOW_UP_{metric}"), metric),
                        "Breakout change": format_metric(row.get(f"DELTA_{metric}"), metric, True)})
    st.dataframe(pd.DataFrame(context), hide_index=True, width="stretch")
    st.caption("MPG and usage rate do not contribute to the breakout trigger or retention classification.")
st.download_button("Download matching player-seasons (CSV)", filtered.to_csv(index=False),
                    file_name="nba_breakout_player_selection.csv", mime="text/csv")
st.caption("Can't find a player? The search includes only seasons that meet the study's definition. It is not a list of every NBA player or every season fans consider a breakout.")

