"""Shared editorial presentation for the research site."""

from html import escape
import streamlit as st
from components.data_loader import GITHUB_URL, paper_path


def apply_style() -> None:
    """Apply a paper, charcoal, and brick-red publication theme."""
    st.markdown("""<style>
    :root { --paper: #F7F4EF; --ink: #1A202C; --muted: #5D6570;
            --line: #D8D3CA; --accent: #8B3A2B; --pale: #EFECE6; }
    .stApp, [data-testid="stHeader"] { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { border-bottom: 1px solid var(--line); }
    .block-container { max-width: 1140px; padding-top: 5rem; padding-bottom: 4rem; }
    .stApp, .stApp p, .stApp button, .stApp input, .stApp label {
      font-family: "Source Sans Pro", "Source Sans 3", sans-serif;
    }
    h1, h2, h3, h4, .hero-title, .hero-figure, .data-value {
      font-family: Georgia, "Times New Roman", serif !important;
      color: var(--ink); letter-spacing: -.035em;
    }
    h1 { font-size: clamp(2.55rem, 5vw, 4.2rem) !important;
         font-weight: 500 !important; line-height: 1.12 !important; }
    h2, h3 { font-weight: 500 !important; line-height: 1.22 !important; }
    p { line-height: 1.72; }
    .wordmark { font-family: Georgia, serif; font-size: 1.06rem; font-weight: 700;
                letter-spacing: -.02em; border-bottom: 1px solid var(--line);
                padding: .1rem 0 1.1rem; margin-bottom: 2.6rem; }
    .wordmark span { color: var(--accent); }
    .section-label, .data-label, .citation-type, .footer-label {
      font-family: ui-monospace, Menlo, Consolas, monospace !important;
      font-size: .72rem; font-weight: 600; letter-spacing: .075em;
      text-transform: uppercase; color: var(--muted);
    }
    .section-label { margin: .15rem 0 1.1rem; }
    .hero { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(270px, .55fr);
            gap: 3.5rem; align-items: end; border-top: 2px solid var(--ink);
            border-bottom: 1px solid var(--line); padding: 3.2rem 0 3.4rem;
            margin: 0 0 2rem; }
    .hero-title { font-size: clamp(3.1rem, 6vw, 5.8rem); line-height: 1.02;
                  font-weight: 500; margin: .8rem 0 1.3rem; }
    .hero-question { font-family: Georgia, serif; font-size: clamp(1.3rem, 2.3vw, 1.7rem);
                     line-height: 1.3; margin: 0 0 1rem; }
    .hero-deck { max-width: 650px; color: var(--muted); font-size: 1.07rem; }
    .hero-result { border-left: 1px solid var(--line); padding-left: 2.3rem; }
    .hero-figure { display: block; font-size: clamp(4rem, 6vw, 6.1rem);
                   line-height: 1; color: var(--accent); white-space: nowrap; }
    .hero-result p { color: var(--muted); margin: 1rem 0 0; font-size: .98rem; }
    .data-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
                  border-bottom: 1px solid var(--line); margin-bottom: 3.5rem; }
    .data-item { padding: .9rem 1.2rem 1.4rem 0; }
    .data-item + .data-item { border-left: 1px solid var(--line); padding-left: 1.4rem; }
    .data-value { display: block; font-size: 2rem; line-height: 1.1; margin-top: .6rem; }
    .essay-panel { border-top: 1px solid var(--line); padding: 1.3rem 0 1.5rem; }
    .essay-panel h2 { font-size: 1.65rem !important; margin: .35rem 0 1rem; }
    .essay-panel p { max-width: 66ch; }
    [data-testid="stMetric"] { background: transparent; border: 0;
      border-top: 1px solid var(--line); border-radius: 0; padding: 1rem 0; box-shadow: none; }
    [data-testid="stMetricLabel"] { white-space: normal; }
    [data-testid="stMetricValue"] { font-family: Georgia, serif; }
    [data-testid="stMetricValue"] > div { white-space: normal; overflow-wrap: anywhere; }
    [data-testid="stPlotlyChart"] { background: #fff; border: 1px solid var(--line);
                                     border-radius: 0; overflow: hidden; }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); }
    blockquote, .takeaway { background: var(--pale); border-left: 2px solid var(--accent);
                            padding: 1rem 1.25rem; margin: 1.5rem 0 2rem; }
    .takeaway p { margin: 0; font-family: Georgia, serif; font-size: 1.12rem; }
    .citation-entry { display: grid; grid-template-columns: minmax(0, 1fr) auto;
                      gap: 1.4rem; align-items: start; border-top: 1px solid var(--line);
                      padding: 1.2rem 0; }
    .citation-entry:last-child { border-bottom: 1px solid var(--line); }
    .citation-title { font-family: Georgia, serif; font-size: 1.24rem; margin: .3rem 0; }
    .citation-detail { color: var(--muted); margin: .3rem 0; }
    .citation-entry a, .stApp a { color: var(--accent); }
    .citation-entry a:hover, .stApp a:hover { text-decoration: underline; }
    .footer { border-top: 1px solid var(--line); margin-top: 4rem; padding-top: 1.2rem;
              color: var(--muted); font-size: .85rem; line-height: 1.55; }
    a:focus-visible, button:focus-visible { outline: 2px solid var(--accent) !important;
                                          outline-offset: 2px; }
    @media (max-width: 760px) {
      .block-container { padding: 5rem 1rem 3rem; }
      .wordmark { margin-bottom: 1.5rem; }
      .hero { grid-template-columns: 1fr; gap: 1.2rem; padding: 2rem 0; }
      .hero-result { border-left: 0; border-top: 1px solid var(--line);
                     padding: 1.3rem 0 0; }
      .data-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .data-item:nth-child(3) { border-left: 0; padding-left: 0; }
      .data-item:nth-child(n+3) { border-top: 1px solid var(--line); }
      .citation-entry { grid-template-columns: 1fr; gap: .3rem; }
    }
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="wordmark">NBA <span>Breakout</span> Lab</div>', unsafe_allow_html=True)


def page_header(section: str, title: str, subtitle: str) -> None:
    """Introduce a page with a quiet section label and serif title."""
    st.markdown(f'<div class="section-label">{escape(section)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.write(subtitle)


def takeaway(text: str) -> None:
    """Set off a short interpretation as a scholarly pull quote."""
    st.markdown(f'<div class="takeaway"><p>{escape(text)}</p></div>', unsafe_allow_html=True)


def show_chart(figure, key: str) -> None:
    """Render Plotly figures with accessible controls and image export."""
    st.plotly_chart(figure, width="stretch", theme=None, key=key,
                    config={"displaylogo": False, "scrollZoom": False,
                            "toImageButtonOptions": {"filename": f"nba_breakout_{key}", "scale": 2}})


def resource_links() -> None:
    """Show source code and a clearly identified manuscript download."""
    st.markdown(f"Sidharth Shyam. (2026). *NBA Breakout Lab* [Research code and data]. [GitHub repository]({GITHUB_URL}).")
    path = paper_path()
    if path:
        mime = "application/pdf" if path.suffix == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        st.download_button(f"Download research manuscript ({path.suffix[1:].upper()})", path.read_bytes(),
                           file_name=path.name, mime=mime)
    else:
        st.caption("The research manuscript is currently unavailable for download.")


def footer() -> None:
    """Keep authorship and historical coverage visible throughout the site."""
    st.markdown('<div class="footer"><span class="footer-label">NBA Breakout Lab</span><br>'
                'Sidharth Shyam · Historical regular-season data through 2022–23. '
                'Results describe player-seasons, not predictions of future performance. '
                'Independent project; no NBA affiliation.</div>', unsafe_allow_html=True)
