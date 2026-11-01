"""The author's motivation and project history."""

import streamlit as st
from components.data_loader import WEBSITE_DIR
from components.styles import page_header, resource_links

page_header("Team", "Basketball curiosity, put to a test.", "An independent research project by Sidharth Shyam.")
st.subheader("Sidharth Shyam · author and researcher")
st.markdown((WEBSITE_DIR / "assets" / "about.md").read_text(encoding="utf-8"))
resource_links()
st.subheader("Feedback and revisions")
st.markdown((WEBSITE_DIR / "assets" / "feedback.md").read_text(encoding="utf-8"))

