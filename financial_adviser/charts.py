"""Plotly figures for the public results dashboard.

The visualization layer never changes a financial projection. All wealth
values are stocks, household adjustments are monthly signed flows, and Monte
Carlo intervals remain a separate view.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from math import ceil

import pandas as pd
import plotly.graph_objects as go


WEALTH_SERIES = (
    "net_worth", "net_worth_real", "cash", "investments", "loan_balance",
    "goal_nominal", "goal_real",
)
DEFAULT_WEALTH_SERIES = ("net_worth", "net_worth_real")

# Color-blind friendly colors, complemented by line dashes.
_COLORS = {
    "net_worth": "#0072B2",
    "net_worth_real": "#D55E00",
    "cash": "#009E73",
    "investments": "#CC79A7",
    "loan_balance": "#7A7A7A",
    "goal_nominal": "#343A40",
    "goal_real": "#986800",
    "child_expenses": "#0072B2",
    "adult_expenses": "#D55E00",
    "dependent_expenses": "#009E73",
    "retirement_income_change": "#CC79A7",
}


def _axis(fig: go.Figure, df: pd.DataFrame, start_year: int,
          currency: str, year_label: str) -> None:
    """Axis uses projected months to avoid fractional-year hover labels."""
    last_month = int(df["month"].iloc[-1])
    step = max(1, ceil((last_month / 12) / 8))
    ticks = list(range(0, last_month + 1, 12 * step))
    fig.update_layout(
        xaxis=dict(
            title=year_label,
            tickmode="array",
            tickvals=ticks,
            ticktext=[str(start_year + month // 12) for month in ticks],
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(title=currency, zeroline=True, zerolinecolor="#9CA3AF"),
        hovermode="x unified",
        legend=dict(orientation="h", x=0, xanchor="left", y=-0.24, yanchor="top"),
        height=385,
        margin=dict(l=8, r=8, t=35, b=105),
    )


def _month_labels(df: pd.DataFrame, start_year: int,
                  translate: Callable[[str], str]) -> list[str]:
    values = []
    for raw in df["month"]:
        month = int(raw)
        if month == 0:
            values.append(translate("chart_initial"))
        else:
            year = start_year + (month - 1) // 12
            month_in_year = (month - 1) % 12 + 1
            values.append(
                f"{year}-{month_in_year:02d} · {translate('chart_month')} {month}"
            )
    return values


def _line(fig: go.Figure, df: pd.DataFrame, y: Iterable[float],
          label: str, color: str, customdata: list[str], currency: str,
          dash: str = "solid", width: float = 2.5) -> None:
    fig.add_trace(go.Scatter(
        x=df["month"], y=y, mode="lines", name=label,
        line=dict(color=color, dash=dash, width=width),
        customdata=customdata,
        hovertemplate="%{customdata}<br>%{y:,.0f} " + currency
                      + "<extra>%{fullData.name}</extra>",
    ))


def wealth_figure(df: pd.DataFrame, goal: float, start_year: int,
                  currency: str, selected: Iterable[str],
                  translate: Callable[[str], str]) -> go.Figure:
    """Only draw selected series; goal lines are dimensionally consistent.

    The *nominal* target is constant in nominal currency. Its real equivalent
    declines as assumed prices rise; each should be compared only with its
    corresponding wealth series.
    """
    requested = tuple(selected)
    unknown = set(requested).difference(WEALTH_SERIES)
    if unknown:
        raise ValueError(f"Unknown chart series: {sorted(unknown)}")
    dates = _month_labels(df, start_year, translate)
    fig = go.Figure()
    y_values = {
        "net_worth": df["net_worth"],
        "net_worth_real": df["net_worth_real"],
        "cash": df["cash"],
        "investments": df["investments"],
        "loan_balance": df["loan_balance"],
        "goal_nominal": [goal] * len(df),
        "goal_real": goal / df["purchasing_power_factor"],
    }
    names = {
        "net_worth": "net_worth",
        "net_worth_real": "net_worth_real",
        "cash": "cash_name",
        "investments": "investments_name",
        "loan_balance": "loan_name",
        "goal_nominal": "target_name",
        "goal_real": "chart_goal_real",
    }
    for field in WEALTH_SERIES:
        if field not in requested:
            continue
        dash = "dot" if field.startswith("goal_") else (
            "dash" if field == "net_worth_real" else "solid"
        )
        _line(fig, df, y_values[field], translate(names[field]),
              _COLORS[field], dates, currency, dash=dash)
    _axis(fig, df, start_year, currency, translate("year"))
    return fig


def household_figure(df: pd.DataFrame, start_year: int, currency: str,
                     translate: Callable[[str], str]) -> go.Figure:
    """Monthly signed adjustments to baseline expenses and income."""
    fields = (
        ("child_expenses", "household_child_delta"),
        ("adult_expenses", "household_adult_delta"),
        ("dependent_expenses", "household_dependent_delta"),
        ("retirement_income_change", "household_retirement_delta"),
    )
    dates = _month_labels(df, start_year, translate)
    fig = go.Figure()
    for field, label in fields:
        # Do not consume space with flat-zero categories.
        if not (df[field] != 0).any():
            continue
        _line(fig, df, df[field], translate(label), _COLORS[field],
              dates, currency, dash="dash" if field == "retirement_income_change" else "solid")
    _axis(fig, df, start_year, currency, translate("year"))
    return fig


def uncertainty_figure(df: pd.DataFrame, mc: object, start_year: int,
                       currency: str, translate: Callable[[str], str]) -> go.Figure:
    """Nominal Monte Carlo quantiles, never mixed with deterministic flows."""
    months = mc.months
    labels = _month_labels(df, start_year, translate)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=mc.p90, mode="lines",
        line=dict(color="rgba(0,114,178,0)", width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=mc.p10, mode="lines", name="P10–P90",
        line=dict(color="rgba(0,114,178,0)", width=0),
        fill="tonexty", fillcolor="rgba(0,114,178,0.17)",
        customdata=labels,
        hovertemplate="%{customdata}<br>%{y:,.0f} " + currency
                      + "<extra>P10</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=mc.p50, mode="lines", name=translate("median"),
        line=dict(color=_COLORS["net_worth"], width=2.8),
        customdata=labels,
        hovertemplate="%{customdata}<br>%{y:,.0f} " + currency
                      + "<extra>%{fullData.name}</extra>",
    ))
    _axis(fig, df, start_year, currency, translate("year"))
    return fig
