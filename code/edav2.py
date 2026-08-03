import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def load_data():
    """
    Loads and returns the four project datasets.
    """
    traditional = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_traditionnal_rs.csv")
    advanced = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_advanced_rs.csv")
    usage = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_usage_rs.csv")
    player_info = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_index.csv")

    return traditional, advanced, usage, player_info


def filter_seasons(data, start_year):
    """
    Filters a season-level dataset to seasons beginning at start_year.
    """
    return data[
        data["SEASON"].str[:4].astype(int) >= start_year
    ].copy()


def print_dataset_size(name, data):
    """
    Prints the number of rows and columns in a dataset.
    """
    rows = len(data)
    columns = len(data.columns)

    print(f"{name}: {rows} rows x {columns} columns")


def print_missing_values(name, data):
    """
    Prints missing-value counts for each column and the dataset total.
    """
    print(f"\n{name}")
    print(data.isnull().sum())
    print(f"Total missing values: {data.isnull().sum().sum()}")


def seven_number_summary(data, columns):
    """
    Returns the required seven-number summary for selected columns.
    """
    summary = data[columns].describe()

    return summary.loc[
        ["mean", "std", "min", "25%", "50%", "75%", "max"]
    ]

def plot_traditional_data(traditional):
    """
    Creates visualizations for the traditional statistics dataset.
    """

    traditional = traditional[traditional["MIN"] > 0].copy()
    traditional["PTS_PER_36"] = (
        traditional["PTS"] / traditional["MIN"] * 36
    )
    # Plot 1: Distribution of minutes per game
    sns.histplot(data=traditional, x="MIN", bins=30)
    plt.title("Distribution of Minutes per Game")
    plt.xlabel("Minutes per Game")
    plt.ylabel("Number of Player-Seasons")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/traditional_minutes_distribution.png")
    plt.close()
    # Plot 2: Minutes per game versus points per 36 minutes
    sns.scatterplot(
        data=traditional,
        x="MIN",
        y="PTS_PER_36",
        alpha=0.4
    )
    plt.title("Minutes per Game vs. Points per 36 Minutes")
    plt.xlabel("Minutes per Game")
    plt.ylabel("Points per 36 Minutes")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/traditional_minutes_vs_points36.png")
    plt.close()

def plot_advanced_data(advanced):
    """
    Creates visualizations for the advanced statistics dataset.
    """

    # Plot 1: Distribution of true shooting percentage
    sns.histplot(data=advanced, x="TS_PCT", bins=30)
    plt.title("Distribution of True Shooting Percentage")
    plt.xlabel("True Shooting Percentage")
    plt.ylabel("Number of Player-Seasons")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/advanced_true_shooting_distribution.png")
    plt.close()

    # Plot 2: Usage rate versus Player Impact Estimate
    sns.scatterplot(
        data=advanced,
        x="USG_PCT",
        y="PIE",
        alpha=0.4
    )
    plt.title("Usage Rate vs. Player Impact Estimate")
    plt.xlabel("Usage Rate")
    plt.ylabel("Player Impact Estimate")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/advanced_usage_vs_pie.png")
    plt.close()

def plot_usage_data(usage):
    """
    Creates visualizations for the usage statistics dataset.
    """

    # Plot 1: Distribution of usage rate
    sns.histplot(data=usage, x="USG_PCT", bins=30)
    plt.title("Distribution of Player Usage Rate")
    plt.xlabel("Usage Rate")
    plt.ylabel("Number of Player-Seasons")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/usage_rate_distribution.png")
    plt.close()

    # Plot 2: Average usage rate by season
    average_usage = (
        usage.groupby("SEASON", as_index=False)["USG_PCT"].mean()
    )
    sns.lineplot(
        data=average_usage,
        x="SEASON",
        y="USG_PCT",
        marker="o",
        label="Average Usage Rate"
    )
    plt.title("Average Player Usage Rate by NBA Season")
    plt.xlabel("Season")
    plt.ylabel("Average Usage Rate")
    plt.xticks(rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/usage_rate_by_season.png")
    plt.close()

def plot_player_info(player_info):
    """
    Creates visualizations for the player information dataset.
    """
    player_info = player_info.copy()

    # Plot 1: Number of players by position
    position_counts = (
        player_info["POSITION"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    position_counts.columns = ["POSITION", "COUNT"]
    sns.barplot(
        data=position_counts,
        x="POSITION",
        y="COUNT"
    )
    plt.title("Number of Players by Listed Position")
    plt.xlabel("Position")
    plt.ylabel("Number of Players")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/player_position_counts.png")
    plt.close()

    # Convert draft number to numeric
    player_info["DRAFT_NUMBER_NUMERIC"] = pd.to_numeric(
        player_info["DRAFT_NUMBER"],
        errors="coerce"
    )

    drafted_players = player_info.dropna(
        subset=["DRAFT_NUMBER_NUMERIC"]
    )

    # Plot 2: Distribution of draft number
    sns.histplot(
        data=drafted_players,
        x="DRAFT_NUMBER_NUMERIC",
        bins=30
    )
    plt.title("Distribution of NBA Draft Selection Number")
    plt.xlabel("Draft Selection Number")
    plt.ylabel("Number of Players")
    plt.tight_layout()
    plt.savefig("/Users/sidharthshyam/nba-breakout-project/figures/player_draft_number_distribution.png")
    plt.close()

def main():
    traditional, advanced, usage, player_info = load_data()

    traditional = filter_seasons(traditional, 1999)
    advanced = filter_seasons(advanced, 1999)
    usage = filter_seasons(usage, 1999)

    print("\nDATASET SIZES")
    print_dataset_size("Traditional stats", traditional)
    print_dataset_size("Advanced stats", advanced)
    print_dataset_size("Usage stats", usage)
    print_dataset_size("Player info", player_info)

    print("\nMISSING VALUES")
    print_missing_values("TRADITIONAL", traditional)
    print_missing_values("ADVANCED", advanced)
    print_missing_values("USAGE", usage)
    print_missing_values("PLAYER INFO", player_info)

    traditional = traditional[traditional["MIN"] > 0].copy()
    traditional["PTS_PER_36"] = (
        traditional["PTS"] / traditional["MIN"] * 36
    )

    traditional_variables = [
        "MIN",
        "PTS_PER_36"
    ]

    advanced_variables = [
        "USG_PCT",
        "TS_PCT",
        "AST_PCT",
        "REB_PCT",
        "DEF_RATING",
        "PIE"
    ]

    print("\nTRADITIONAL VARIABLES OF INTEREST")
    print(seven_number_summary(
        traditional,
        traditional_variables
    ))

    print("\nADVANCED VARIABLES OF INTEREST")
    print(seven_number_summary(
        advanced,
        advanced_variables
    ))

    print("\nPLAYER POSITION COUNTS")
    print(player_info["POSITION"].value_counts(dropna=False))

    plot_traditional_data(traditional)
    plot_advanced_data(advanced)
    plot_usage_data(usage)
    plot_player_info(player_info)


if __name__ == "__main__":
    main()

