"""Plotly figures with consistent units, colors, and sample-size hover labels."""

from textwrap import wrap

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.data_loader import METRICS, OUTCOMES, readable_profile

INK = "#1A202C"
ACCENT = "#8B3A2B"
GRAY = "#9A9A96"
OUTCOME_COLORS = {"Regressed": GRAY, "Sustained at least 80%": ACCENT, "Improved further": INK}


def polish(fig: go.Figure, title: str, height: int = 390) -> go.Figure:
    """Give each chart generous margins and high-contrast labels."""
    fig.update_layout(title={"text": "<br>".join(wrap(title, width=30)),
                             "font": {"family": "Georgia, serif", "size": 18, "color": INK}, "x": .03},
                      font={"family": "Source Sans Pro, sans-serif", "size": 13, "color": INK},
                      paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", height=height,
                      margin={"l": 24, "r": 32, "t": 90, "b": 60},
                      hoverlabel={"bgcolor": INK, "font_color": "white"},
                      legend_title_text="", bargap=.35)
    fig.update_xaxes(showgrid=False, automargin=True, zeroline=False)
    fig.update_yaxes(gridcolor="#E7E3DD", automargin=True, zeroline=False)
    return fig


def outcome_chart(summary: pd.DataFrame) -> go.Figure:
    """Show the three mutually exclusive saved baseline outcomes."""
    data = summary.set_index("RESULT").reindex(OUTCOMES).reset_index()
    data["LABEL"] = data.RESULT.replace({"Sustained at least 80%": "Sustained<br>80–100%", "Improved further": "Improved<br>further"})
    fig = px.bar(data, x="LABEL", y="PERCENT", color="RESULT", color_discrete_map=OUTCOME_COLORS,
                 text="PERCENT", custom_data=["COUNT", "RESULT"],
                 labels={"LABEL": "Following-season outcome", "PERCENT": "Share of eligible breakouts (%)"})
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{customdata[1]}<br>%{y:.1f}% · n=%{customdata[0]}<extra></extra>")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(range=[0, max(65, data.PERCENT.max() + 12)])
    return polish(fig, "What happened in the following season?")


def player_chart(row: pd.Series, metric: str) -> go.Figure:
    """Compare one metric on its own scale across three consecutive seasons."""
    dimension, label, color = METRICS[metric]
    values = [row.get(f"PREV_{metric}"), row.get(metric), row.get(f"FOLLOW_UP_{metric}")]
    values = [None if pd.isna(v) else float(v) * (100 if metric.endswith("PCT") else 1) for v in values]
    seasons = [row.get("PREV_SEASON"), row.get("SEASON"), row.get("FOLLOW_UP_SEASON")]
    seasons = ["Unavailable" if pd.isna(v) else str(v) for v in seasons]
    fig = go.Figure(go.Scatter(x=["Previous", "Breakout", "Following"], y=values,
                               mode="lines+markers+text", connectgaps=False,
                               text=[f"{v:.1f}" if v is not None else "" for v in values],
                               textposition="top center", customdata=seasons,
                               line={"color": color, "width": 3}, marker={"size": 11},
                               hovertemplate="%{x} · %{customdata}<br>%{y:.2f}<extra>" + label + "</extra>"))
    fig.update_yaxes(title=label, rangemode="tozero")
    fig.update_xaxes(title="Season relative to breakout")
    if any(v is not None for v in values):
        fig.update_yaxes(range=[0, max(v for v in values if v is not None) * 1.22])
    return polish(fig, f"{dimension}: before, during, and after", 360)


def dimension_chart(data: pd.DataFrame) -> go.Figure:
    """Show median retention as a percent of the original improvement."""
    data = data.copy()
    data["Dimension"] = data.DIMENSION.map(lambda m: METRICS[m][0])
    data["Retention (%)"] = data.MEDIAN_RETENTION * 100
    fig = px.bar(data, x="Dimension", y="Retention (%)", color="Dimension", text="Retention (%)",
                 color_discrete_map={v[0]: v[2] for v in METRICS.values()}, custom_data=["COUNT"])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                      hovertemplate="%{x}<br>%{y:.1f}% median retained · n=%{customdata[0]}<extra></extra>")
    fig.update_traces(textposition="inside", insidetextanchor="middle", textfont_color="white")
    fig.update_layout(showlegend=False)
    fig.add_hline(y=80, line_dash="dot", line_color=INK)
    fig.update_yaxes(range=[0, 100], title="Median improvement retained (%)")
    return polish(fig, "Which improvements lasted? · 80% reference line")


def group_chart(data: pd.DataFrame, group: str, title: str,
                order: list | None = None, intervals: pd.DataFrame | None = None) -> go.Figure:
    """Compare group rates and, when available, saved player-clustered intervals."""
    data = data.copy()
    data["Group"] = data[group].astype(str)
    if intervals is not None:
        selected = intervals[intervals.VARIABLE == group]
        data = data.merge(selected[["GROUP", "CI_LOWER", "CI_UPPER"]], left_on="Group", right_on="GROUP", how="left", validate="one_to_one")
        data["upper_error"] = data.CI_UPPER - data.SUSTAINABILITY_RATE
        data["lower_error"] = data.SUSTAINABILITY_RATE - data.CI_LOWER
    fig = px.bar(data, x="Group", y="SUSTAINABILITY_RATE", text="SUSTAINABILITY_RATE",
                 custom_data=["COUNT", "MEDIAN_RETENTION"],
                 category_orders={"Group": [str(v) for v in order]} if order else None,
                 error_y="upper_error" if intervals is not None else None,
                 error_y_minus="lower_error" if intervals is not None else None,
                 color_discrete_sequence=[INK])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}<br>%{y:.1f}% sustained or improved<br>n=%{customdata[0]}<br>Median retention: %{customdata[1]:.1%}<extra></extra>")
    if intervals is not None:
        fig.update_traces(textposition="inside", insidetextanchor="middle", textfont_color="white")
    axis_titles = {"BREAKOUT_DIMENSIONS": "Number of qualifying dimensions", "AGE_GROUP": "Age group",
                   "EXPERIENCE_GROUP": "Prior NBA experience", "POSITION_GROUP": "Primary position",
                   "DRAFT_GROUP": "Draft group"}
    # Force category axes so dimension counts remain 2/3/4, not 1.5/2/2.5 etc.
    fig.update_xaxes(title=axis_titles.get(group, "Group"), type="category")
    if order:
        fig.update_xaxes(categoryorder="array", categoryarray=[str(v) for v in order])
    fig.update_yaxes(title="Sustained or improved (%)", range=[0, 100])
    return polish(fig, title, 410)


def profile_chart(data: pd.DataFrame) -> go.Figure:
    """Sort labels and bars together; include sample sizes and unrounded rates."""
    data = data.sort_values("SUSTAINABILITY_RATE").copy()
    data["Profile"] = data.BREAKOUT_PROFILE.map(readable_profile).str.replace(" + ", " +<br>", regex=False)
    fig = px.bar(data, x="SUSTAINABILITY_RATE", y="Profile", orientation="h", text="SUSTAINABILITY_RATE",
                 custom_data=["COUNT", "MEDIAN_RETENTION"], color_discrete_sequence=[ACCENT])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>%{x:.1f}% sustained or improved<br>n=%{customdata[0]}<br>Median retention: %{customdata[1]:.1%}<extra></extra>")
    fig.update_xaxes(title="Sustained or improved (%)", range=[0, 100])
    fig.update_yaxes(title=None)
    return polish(fig, "Sustainability by breakout profile", max(450, len(data) * 78 + 90))


def sensitivity_chart(data: pd.DataFrame, selected: pd.Series) -> go.Figure:
    """Compare all 18 breakout definitions at the selected retention standard."""
    data = data[(data.RETENTION_THRESHOLD - selected.RETENTION_THRESHOLD).abs() < 1e-8].copy()
    data = data.sort_values(["MINUTE_CUTOFF", "PERCENTILE_THRESHOLD", "MIN_DIMENSIONS"])
    data["Definition"] = data.apply(lambda r: f"{int(r.MINUTE_CUTOFF)} min · P{r.PERCENTILE_THRESHOLD * 100:.0f} · ≥{int(r.MIN_DIMENSIONS)} dims", axis=1)
    chosen = (data.MINUTE_CUTOFF == selected.MINUTE_CUTOFF) & (data.PERCENTILE_THRESHOLD == selected.PERCENTILE_THRESHOLD) & (data.MIN_DIMENSIONS == selected.MIN_DIMENSIONS)
    fig = go.Figure(go.Scatter(x=data.SUSTAINABILITY_RATE, y=data.Definition, mode="markers",
                               marker={"size": [13 if b else 8 for b in chosen], "color": [ACCENT if b else INK for b in chosen]},
                               customdata=data[["BREAKOUTS_FOUND", "ELIGIBLE_FOLLOW_UPS"]].to_numpy(),
                               hovertemplate="%{y}<br>%{x:.1f}% sustained<br>%{customdata[0]} detected · %{customdata[1]} eligible<extra></extra>"))
    fig.add_vline(x=50, line_dash="dot", line_color="#9A9A96")
    fig.update_xaxes(title="Sustained or improved (%)", range=[0, 65])
    fig.update_yaxes(title=None, autorange="reversed")
    return polish(fig, f"18 definitions · {selected.RETENTION_THRESHOLD:.0%} retention", 660)


def sensitivity_heatmap(data: pd.DataFrame, selected: pd.Series) -> go.Figure:
    """Show the nine minute/percentile combinations with other settings held fixed."""
    data = data[(data.MIN_DIMENSIONS == selected.MIN_DIMENSIONS) &
                ((data.RETENTION_THRESHOLD - selected.RETENTION_THRESHOLD).abs() < 1e-8)]
    pivot = data.pivot(index="MINUTE_CUTOFF", columns="PERCENTILE_THRESHOLD", values="SUSTAINABILITY_RATE").sort_index()
    fig = go.Figure(go.Heatmap(z=pivot.to_numpy(), x=[f"{p:.0%}" for p in pivot.columns],
                               y=[str(m) for m in pivot.index], zmin=0, zmax=100,
                               colorscale=[[0, "#F7F4EF"], [.5, "#B9A59D"], [1, "#8B3A2B"]],
                               texttemplate="%{z:.1f}%", showscale=False, xgap=5, ygap=5,
                               hovertemplate="%{y} minutes · %{x} percentile<br>%{z:.1f}% sustained<extra></extra>"))
    fig.update_xaxes(title="Breakout percentile threshold", type="category")
    fig.update_yaxes(title="Minimum minutes", type="category")
    return polish(fig, f"Threshold combinations · ≥{int(selected.MIN_DIMENSIONS)} dimensions", 390)
