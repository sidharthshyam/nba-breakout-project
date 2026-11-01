"""Research manuscript, source data, and reproducibility records."""

import pandas as pd
import streamlit as st
from components.data_loader import DATA_SOURCE_URL, FILES, GITHUB_URL, paper_path
from components.styles import page_header

page_header("Publications", "Read the work behind the results.",
            "The manuscript is an unpublished research draft. The source dataset and project code are listed separately so their roles remain clear.")

st.markdown('''<div class="citation-entry"><div>
  <div class="citation-type">Research manuscript · draft</div>
  <div class="citation-title">Analysis of NBA Breakout Seasons</div>
  <p class="citation-detail">Shyam, S. (2026). <em>Analysis of NBA Breakout Seasons</em>
  [Unpublished research manuscript]. NBA Breakout Lab.</p>
</div><div class="citation-type">01</div></div>''', unsafe_allow_html=True)
manuscript = paper_path()
if manuscript:
    mime = "application/pdf" if manuscript.suffix == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    st.download_button(f"Download manuscript ({manuscript.suffix[1:].upper()})", manuscript.read_bytes(),
                       file_name=manuscript.name, mime=mime)
else:
    st.caption("The manuscript file is currently unavailable.")
st.caption("This is the existing sensitivity-analysis draft. Its wording includes the broader 2000–01 study window; detected breakouts actually begin in 2001–02.")

st.markdown(f'''<div class="citation-entry"><div>
  <div class="citation-type">Data source</div>
  <div class="citation-title">NBA Statistics Repository</div>
  <p class="citation-detail">Brescou, T. (n.d.). <em>NBA Statistics Repository</em>
  [Data set]. GitHub. <a href="{DATA_SOURCE_URL}">View original source</a>.</p>
</div><div class="citation-type">02</div></div>''', unsafe_allow_html=True)

st.markdown(f'''<div class="citation-entry"><div>
  <div class="citation-type">Research code and interactive application</div>
  <div class="citation-title">NBA Breakout Lab</div>
  <p class="citation-detail">Shyam, S. (2026). <em>NBA Breakout Lab</em>
  [Computer software and research outputs]. GitHub.
  <a href="{GITHUB_URL}">Inspect repository</a>.</p>
</div><div class="citation-type">03</div></div>''', unsafe_allow_html=True)

st.subheader("Data records used on this site")
st.write("The figures and tables read saved analysis outputs. These are the principal files behind the interactive views; the full file inventory and regeneration instructions are in the repository README.")
records = [
    ("Detected player-seasons", FILES["breakouts"]),
    ("Eligible follow-ups and retention", FILES["eligible"]),
    ("Following-season outcome summary", FILES["outcomes"]),
    ("Definition sensitivity", FILES["sensitivity"]),
    ("Bootstrap intervals", FILES["intervals"]),
]
st.dataframe(pd.DataFrame(records, columns=["Record", "Saved file in code/"]),
             hide_index=True, width="stretch")
st.page_link("pages/3_Research_Findings.py", label="Read findings and inspect the charts →")
st.page_link("pages/4_Methodology.py", label="Review definitions and limitations →")
