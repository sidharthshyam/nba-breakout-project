import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#Loading stat datasets
traditional = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_traditionnal_rs.csv")
advanced = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_advanced_rs.csv")
usage = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_stats_usage_rs.csv")
player_info = pd.read_csv("/Users/sidharthshyam/nba-breakout-project/data/raw/player_index.csv")

traditional = traditional[
    traditional["SEASON"].str[:4].astype(int) >= 1999
]

advanced = advanced[
    advanced["SEASON"].str[:4].astype(int) >= 1999
]

usage = usage[
    usage["SEASON"].str[:4].astype(int) >= 1999
]

#Rows and Columns of each Dataset
rows_traditional = len(traditional)
columns_traditional = len(traditional.columns)
print(f"Traditional stats: {rows_traditional} Rows X {columns_traditional} Columns")

rows_advanced = len(advanced)
columns_advanced = len(advanced.columns)
print(f"Advanced stats: {rows_advanced} Rows X {columns_advanced} Columns")

rows_usage = len(usage)
columns_usage = len(usage.columns)
print(f"Usage stats: {rows_usage} Rows X {columns_usage} Columns")

rows_info = len(player_info)
columns_info = len(player_info.columns)
print(f"Player Info stats: {rows_info} Rows X {columns_info} Columns")

#Finding missing values
print("Missing Values in each dataset:\n")
print("TRADITIONAL")
print(traditional.isnull().sum())
print(f"Total traditional stats missing values: {traditional.isnull().sum().sum()}")

print("ADVANCED")
print(advanced.isnull().sum())
print(f"Total advanced stats missing values: {advanced.isnull().sum().sum()}")

print("USAGE")
print(usage.isnull().sum())
print(f"Total usage stats missing values: {usage.isnull().sum().sum()}")

print("PLAYER_INFO")
print(player_info.isnull().sum())
print(f"Total player info stats missing values: {player_info.isnull().sum().sum()}")