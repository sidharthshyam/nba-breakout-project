# NBA Breakout Lab

Interactive Streamlit companion to the NBA breakout-sustainability research.
The primary navigation has Abstract, Methodology, Findings & Data, Publications,
and Team. Player Explorer and Definition Lab remain available through links in
the research pages.
The app reads the existing research outputs; it does not run the full research
pipeline when someone changes a filter. No database, API key, or account is
required to run it locally.

## Install and run

Use **Python 3.12** (the tested version). Clone/download the **entire repository**,
not only the website folder. From the repository root:

```bash
python3 -m venv website/.venv
source website/.venv/bin/activate
python -m pip install -r website/requirements.txt
cd website
python -m streamlit run app.py --server.address 127.0.0.1
```

Open the local URL shown in the terminal, normally http://localhost:8501.
On Windows, activate using `website\.venv\Scripts\activate` instead. Stop the
server with Ctrl+C. Starting from `website` loads its `.streamlit/config.toml`
theme. You can also run `python -m streamlit run website/app.py` from the repository
root; data paths still work, but Streamlit searches the working directory for
theme configuration. The app's shared styles still apply.

No absolute-path replacement is needed in the website. Paths are resolved from
the Python files. Data are cached for five minutes; restart the app to reload
changed CSVs immediately. The local `.venv` is ignored by Git and must not be
uploaded.

## Required research inputs

The website reads these files from `code/`:

- `nba_breakout_seasons.csv`: all 808 baseline detections.
- `nba_breakout_sustainability.csv`: 660 eligible follow-ups with detailed metrics,
  outcomes, retention, and characteristics.
- `sustainability_summary.csv`: three baseline outcome counts and percentages.
- `dimension_summary.csv`, `profile_summary.csv`, `dimension_count_summary.csv`:
  dimension and profile findings.
- `age_summary.csv`, `experience_summary.csv`, `position_summary.csv`,
  `draft_summary.csv`, `physical_summary.csv`: player-characteristic findings.
- `robustness_outputs/sensitivity_analysis.csv`: all 54 tested specifications.
- `robustness_outputs/attrition_summary.csv`: follow-up coverage.
- `robustness_outputs/confidence_intervals.csv`: existing bootstrap intervals.

It also reads `data/raw/player_stats_traditionnal_rs.csv`,
`player_stats_advanced_rs.csv`, and `player_stats_usage_rs.csv` to verify the
eligible-pair count and attach context for unevaluated follow-ups. Keep the
original spelling `traditionnal`. Existing research data use MPG in traditional
and TOTAL_MIN in usage. The website does not import ba.py or sa.py at runtime.

The optional paper download is
`website/assets/nba_breakout_paper_with_sensitivity.docx`. You can replace it with
an updated version or add a PDF of the same stem; PDF is preferred if both exist.
The copy currently included is the existing sensitivity-analysis manuscript,
provided unchanged. Removing it produces an unavailable message rather than an
app error. See DATA_AUDIT.md for its date-window clarification.

## Regenerate inputs if necessary

The original research programs still use local absolute paths. Follow the root
README's path-setup section to update those paths on another machine. Do this
only when regenerating results, not simply when running the website. Existing
outputs are enough for deployment.

Install the research dependencies into your activated environment:

```bash
python -m pip install numpy matplotlib seaborn
```

Then, from the repository root:

```bash
cd code
python ba.py
python sa.py
python robustness_analysis.py
```

These commands overwrite research outputs with new results. Review intentional
method changes before regenerating them. Restart the website afterward and rerun
its tests; baseline snapshot assertions must be revisited if the dataset or
research definition intentionally changes.

## Verification

From the repository root with the environment activated:

```bash
python -m unittest discover -s website -p 'test_website.py' -v
python -B code/test_project.py
python -B code/test_eda.py
python -B code/test_robustness.py
```

The existing research tests require numpy, matplotlib, and seaborn as above and
the path setup documented in the root README. Website checks use the standard
library's unittest plus Streamlit AppTest. They cover data joins, exact baseline
counts, summary reconciliation, retention calculations, percentage units, all
54 sensitivity settings, page rendering, changed controls, empty results, and
missing optional context. Tests do not overwrite CSV files.

## Files and responsibilities

| Python file | Purpose |
| --- | --- |
| `app.py` | Navigation, shared layout, and actionable input-file errors |
| `pages/0_Home.py` | Editorial abstract, verified headline metrics, outcome chart, research-tool links |
| `pages/1_Player_Explorer.py` | Baseline filters, player and season selection, three-season comparisons, CSV download |
| `pages/2_Definition_Lab.py` | Precomputed specification selection, heatmap, comparison chart |
| `pages/3_Research_Findings.py` | Three research-question views, sample sizes, uncertainty intervals |
| `pages/4_Methodology.py` | Definitions, formula, coverage, limitations, provenance |
| `pages/5_About.py` | Author text, resources, and feedback history |
| `pages/6_Publications.py` | Manuscript, data source, code citations, and output inventory |
| `components/__init__.py` | Declares the shared components package |
| `components/data_loader.py` | Cached relative-path reads, joins, validation, labels, filtering |
| `components/charts.py` | Reusable Plotly figures |
| `components/styles.py` | Theme, headings, resource links, chart display |
| `test_website.py` | Data integrity and Streamlit interaction tests |

Other editable files: `assets/about.md` (bio/contact), `assets/feedback.md`
(actual feedback history), `.streamlit/config.toml` (theme), `requirements.txt`
(tested runtime versions), and `DATA_AUDIT.md` (source verification).
The editorial theme uses Streamlit's bundled Source Sans and Source Code fonts,
Georgia for headings, a cream background, charcoal text, and one brick-red
accent. It does not require a third-party font service.

## Public website and updates

The public app is [nba-breakout-lab.streamlit.app](https://nba-breakout-lab.streamlit.app/).
It runs from the `main` branch of this repository with `website/app.py` as its
entrypoint and Python 3.12 as its runtime.

To update it, review the changed content for public release, then commit and
push the website and any changed research outputs. Streamlit Community Cloud
redeploys from GitHub. Do not commit `.venv`, caches, secrets, or local test
screenshots. The runtime dependencies are in `website/requirements.txt`; the
hosted theme is configured by the repository-root `.streamlit/config.toml`.
After an update, check the homepage, navigation, downloads, player filters, and
definition controls at the public URL.

Official references: [multipage navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation),
[AppTest](https://docs.streamlit.io/develop/api-reference/app-testing),
and [Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Interpretation and limits

The Player Explorer always uses the baseline definition. Definition Lab settings
change aggregate sensitivity results only; they do not change the player list.
Unevaluated follow-ups remain unevaluated. Percentages on summary charts already
use 0–100 units. Metric percentages, percentile ranks, and retention are stored
as proportions and formatted once. The sensitivity range is not a confidence
interval, and neither it nor the bootstrap intervals establishes causation.

The project is an independent historical analysis with no NBA affiliation.
No professional endorsement or publication acceptance is claimed.

