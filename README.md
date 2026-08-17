# NBA Breakout Sustainability Project

This project identifies NBA breakout seasons and examines whether those
improvements are sustained in the following season. It also studies how
performance dimensions involved in each breakout and player
characteristics relate to sustainability.

## Required software and libraries

Use Python 3.10 or later. Install the required libraries by running:


python3 -m pip install pandas numpy matplotlib seaborn plotly


No data must be downloaded separately. The required CSV files are included in
the `data/raw` directory.

## Submitted Python files

- `code/ba.py`: Breakout Analysis(ba) file. Loads and merges the season-level statistics, creates
  consecutive player-season pairs, calculates year-over-year changes and
  within-season percentile ranks, identifies breakout seasons, and saves the
  breakout-season dataset.
- `code/sa.py`: Sustainability Analysis(sa) file. Performs the sustainability analysis for all three research
  questions. It adds following-season statistics, calculates retention,
  classifies sustainability, summarizes breakout dimensions and profiles,
  adds player characteristics, produces figures, and saves the final result
  tables. It also creates the interactive Plotly visualization.
- `code/eda.py`: Conducts the exploratory data analysis and generates the EDA
  summary output and figures.
- `code/test_project.py`: Tests the main breakout and sustainability functions
  using a small controlled dataset.
- `code/test_eda.py`: Tests selected data-processing functions from `eda.py`.

## Data files

- `data/raw/player_stats_traditionnal_rs.csv`: Traditional player-season
  statistics.
- `data/raw/player_stats_advanced_rs.csv`: Advanced player-season statistics.
- `data/raw/player_stats_usage_rs.csv`: Player usage and total-minute data.
- `data/raw/player_index.csv`: Player position, height, weight, draft, and
  career information.
- `data/test/test_stats.csv`: Small controlled dataset used by
  `test_project.py`.

## Path setup

Some paths in the Python files use the original project location:

/Users/sidharthshyam/nba-breakout-project/

Before running the project on another computer, replace that text with the
absolute path to the downloaded `nba-breakout-project` directory. Check the
following locations:

- The three `pd.read_csv` paths in `code/ba.py`
- Data and figure paths in `code/eda.py`
- Data and figure paths in `code/sa.py`
- `TEST_DATA` near the top of `code/test_project.py`

Make sure the project contains `data/raw`, `data/test`, `figures`, and `code`
directories before running the programs.

## How to reproduce the project

Open a terminal and enter the code directory. Replace the path below if the
project is stored elsewhere:


cd /Users/sidharthshyam/nba-breakout-project/code


Run the exploratory data analysis:


python3 eda.py


Run the breakout-season analysis:


python3 ba.py


This creates `nba_breakout_seasons.csv` in the `code` directory.

Run the complete sustainability analysis:


python3 sa.py


This creates the player-level sustainability dataset and the summary CSV files
for the three research questions in the `code` directory. It also creates the
static figures and the interactive Plotly file in the `figures` directory.

To view the interactive Plotly visualization, open the following file in a web
browser rather than a text editor:

figures/interactive_sustainability_by_profile.html

## How to run the tests

From the `code` directory, run:


python3 test_eda.py
python3 test_project.py


Each test program prints a confirmation message when all its assertions pass.

## Reproduced outputs

The principal outputs are:

- `code/nba_breakout_seasons.csv`
- `code/nba_breakout_sustainability.csv`
- `code/sustainability_summary.csv`
- `code/dimension_summary.csv`
- `code/profile_summary.csv`
- `code/dimension_count_summary.csv`
- `code/age_summary.csv`
- `code/experience_summary.csv`
- `code/position_summary.csv`
- `code/draft_summary.csv`
- `code/physical_summary.csv`
- PNG visualizations in `figures`
- `figures/interactive_sustainability_by_profile.html`

Running the programs again replaces output files with the same names.
