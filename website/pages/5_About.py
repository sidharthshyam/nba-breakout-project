"""The author's motivation, editable profile, and transparent project history."""

import streamlit as st
from components.data_loader import WEBSITE_DIR
from components.styles import page_header, resource_links

page_header("Team", "Basketball curiosity, put to a test.", "An independent research project by Sidharth Shyam.")
st.subheader("Sidharth Shyam · author and researcher")
st.markdown((WEBSITE_DIR / "assets" / "about.md").read_text(encoding="utf-8"))
resource_links()
st.subheader("Feedback and revisions")
st.markdown((WEBSITE_DIR / "assets" / "feedback.md").read_text(encoding="utf-8"))
st.subheader("Tools and collaboration")
st.write("The research uses Python and pandas, with Matplotlib, seaborn, and Plotly for visualization. This website uses Streamlit and Plotly. ChatGPT/Codex assisted with code development, debugging, writing, and website implementation. The author is responsible for reviewing the methods, code, and interpretation. The manuscript is a research draft; this website does not claim journal acceptance or professional endorsement.")

