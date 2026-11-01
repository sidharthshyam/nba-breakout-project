"""Run with: python -m streamlit run website/app.py."""

import streamlit as st
from components.styles import apply_style, footer

st.set_page_config(page_title="NBA Breakout Lab", layout="wide")
pages = [
    st.Page("pages/0_Home.py", title="Abstract", default=True),
    st.Page("pages/4_Methodology.py", title="Methodology", url_path="methodology"),
    st.Page("pages/3_Research_Findings.py", title="Findings & Data", url_path="findings"),
    st.Page("pages/6_Publications.py", title="Publications", url_path="publications"),
    st.Page("pages/5_About.py", title="Team", url_path="team"),
    st.Page("pages/1_Player_Explorer.py", title="Player Explorer", url_path="players", visibility="hidden"),
    st.Page("pages/2_Definition_Lab.py", title="Definition Lab", url_path="definitions", visibility="hidden"),
]
page = st.navigation(pages, position="top")
apply_style()
try:
    page.run()
except (FileNotFoundError, ValueError, KeyError) as error:
    st.error(f"This page could not load its research data. {error}")
    st.info("Restore the required outputs described in website/README.md, then restart the app. No results have been substituted.")
footer()

