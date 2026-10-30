"""Plotly figures for the public results dashboard.

The visualization layer never changes a financial projection. All wealth
values are stocks, household adjustments are monthly signed flows, and Monte
Carlo intervals remain a separate view.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from math import ceil

import pandas as pd
import plotly.graph_objects as go

from .models import Plan


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
        if field.startswith("goal_") and goal <= 0:
            continue  # No meaningful positive target was configured.
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


@dataclass(frozen=True)
class EventMarker:
    month: int
    label: str
    kind: str


MAX_EVENT_LINES = 12


def event_markers(plan: Plan) -> tuple[EventMarker, ...]:
    """Build chronological, user-readable milestones from a saved scenario.

    An end marker marks the first month AFTER a temporary item stops
    affecting flows, rather than the last month still affected by it.
    """
    n = plan.years * 12
    marks: list[EventMarker] = []

    def add(month: int, label: str, kind: str) -> None:
        if 1 <= month <= n:
            marks.append(EventMarker(month, label, kind))

    for event in plan.life_events:
        add(event.first_month, event.label, "event_start")
        add(event.first_month + event.duration_months, event.label, "event_end")
    for item in plan.one_offs:
        add(item.month, item.description, "oneoff")
    for child in plan.children:
        add(child.arrival_month, child.label, "child_arrival")
        add(child.arrival_month +
            12 * (child.support_until_age - child.age_years),
            child.label, "child_support_end")
    for dependent in plan.dependents:
        add(dependent.first_month, dependent.label, "dependent_start")
        add(dependent.first_month + dependent.duration_months,
            dependent.label, "dependent_end")
    for adult in plan.adults:
        if adult.age_years < adult.retirement_age:
            add(1 + 12 * (adult.retirement_age - adult.age_years),
                adult.label, "retirement")
    # Multiple events can occur in the same month. Keep every item in the
    # accessible list while drawing just one vertical line per month.
    return tuple(sorted(marks, key=lambda m: (m.month, m.kind, m.label)))


def overlay_event_markers(fig: go.Figure,
                          markers: Iterable[EventMarker]) -> tuple[int, int]:
    """Draw up to 12 unobtrusive date markers, never changing chart values.

    Returns (drawn_unique_months, total_unique_months); the UI can explain
    whether a long list is intentionally abbreviated on the graphic.
    """
    distinct = sorted({event.month for event in markers})
    for month in distinct[:MAX_EVENT_LINES]:
        fig.add_vline(
            x=month, line_width=1.25, line_dash="dot",
            line_color="#6B7280", opacity=0.65,
        )
    return min(len(distinct), MAX_EVENT_LINES), len(distinct)


def comparison_figure(cases: Iterable[object], start_year: int, currency: str,
                      translate: Callable[[str], str], goal: float) -> go.Figure:
    """Compare only nominal wealth at the *same* selected horizon."""
    variants = tuple(cases)
    if not variants:
        raise ValueError("At least one comparison is required")
    reference = variants[0].projection
    dates = _month_labels(reference, start_year, translate)
    fig = go.Figure()
    palette = {
        "scenario_lower": "#D55E00",
        "scenario_base": "#0072B2",
        "scenario_higher": "#009E73",
        "scenario_no_events": "#7A7A7A",
        "scenario_events_more": "#CC79A7",
    }
    for case in variants:
        df = case.projection
        if len(df) != len(reference):
            raise ValueError("Scenario horizons must agree")
        key = case.key
        _line(fig, df, df["net_worth"], translate(key),
              palette[key], dates, currency,
              dash="solid" if key == "scenario_base" else "dash",
              width=3.2 if key == "scenario_base" else 2.0)
    _axis(fig, reference, start_year, currency, translate("year"))
    if goal > 0:
        fig.add_hline(
            y=goal, line=dict(color="#6B7280", dash="dot", width=1.1),
        )
    return fig



def stress_liquidity_figure(evaluation: object, start_year: int,
                            currency: str,
                            translate: Callable[[str], str]) -> go.Figure:
    """Compare baseline and stressed *cash* without implying likelihood.

    Only the stressed scenario's additional life event is shaded in time;
    the faint region below zero represents an unfunded shortfall, not debt
    automatically available to the household.
    """
    base = evaluation.baseline
    stressed = evaluation.stressed
    if len(base) != len(stressed) or not base.month.equals(stressed.month):
        raise ValueError("Stress and baseline must share the same months")
    labels = _month_labels(base, start_year, translate)
    fig = go.Figure()
    _line(fig, base, base.cash, translate("scenario_base"),
          "#0072B2", labels, currency, width=2.8)
    _line(fig, stressed, stressed.cash,
          translate("preset_" + evaluation.impact.key), "#D55E00",
          labels, currency, dash="dash", width=2.8)
    _axis(fig, base, start_year, currency, translate("year"))
    fig.add_hline(y=0, line=dict(color="#6B7280", dash="dot", width=1.2))
    lowest = min(float(base.cash.min()), float(stressed.cash.min()))
    if lowest < 0:
        fig.add_hrect(
            y0=lowest * 1.04, y1=0,
            fillcolor="#D55E00", opacity=0.07, line_width=0,
        )
    event = evaluation.impact.event
    fig.add_vrect(
        x0=event.first_month - 0.5,
        x1=event.first_month + event.duration_months - 0.5,
        fillcolor="#D55E00", opacity=0.06, line_width=0,
    )
    return fig



def resilience_figure(
    df: pd.DataFrame, measure: object,
    start_year: int, currency: str, translate: Callable[[str], str],
) -> go.Figure:
    """Cash comparison for a user-entered one-off expense (no probabilities)."""
    if len(df) != len(measure.baseline_cash) or len(df) != len(measure.stressed_cash):
        raise ValueError("Cash paths do not match the projection horizon")
    dates = _month_labels(df, start_year, translate)
    fig = go.Figure()
    _line(fig, df, measure.baseline_cash, translate("scenario_base"),
          _COLORS["net_worth"], dates, currency, width=2.8)
    if measure.shock_amount > 0:
        _line(fig, df, measure.stressed_cash, translate("resilience_expense_case"),
              _COLORS["net_worth_real"], dates, currency, dash="dash",
              width=2.8)
    _axis(fig, df, start_year, currency, translate("year"))
    fig.add_hline(y=0, line=dict(color="#6B7280", dash="dot", width=1.2))
    lowest = min(measure.baseline_minimum_cash, measure.shock_minimum_cash)
    if lowest < 0:
        fig.add_hrect(y0=lowest * 1.04, y1=0, fillcolor="#D55E00",
                      opacity=0.07, line_width=0)
    if measure.shock_amount > 0:
        fig.add_vline(
            x=measure.shock_month,
            line=dict(color="#D55E00", dash="dot", width=1.2),
        )
    return fig



SENSITIVITY_METRICS = (
    "final_real_change", "final_nominal_change", "minimum_cash_change",
)


def assumption_sensitivity_figure(
    report: object, metric: str, currency: str,
    translate: Callable[[str], str],
) -> go.Figure:
    """A signed impact bar chart, not an input-importance ranking.

    Bars represent actual simulated changes versus the same-horizon baseline.
    Different inputs are perturbed on distinct scales (+10% vs +1pp);
    therefore bar lengths must not be interpreted as standardized importance.
    """
    if metric not in SENSITIVITY_METRICS:
        raise ValueError("Unsupported sensitivity output")
    impacts = report.impacts
    if not impacts:
        raise ValueError("No meaningful sensitivity perturbations")
    labels = [
        translate("sens_field_" + item.field)
        + (" (" + f"{item.change_size:+g}" +
           (translate("sens_pct") if item.kind == "amount" else translate("sens_pp")) + ")")
        for item in impacts
    ]
    values = [float(getattr(item, metric)) for item in impacts]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=[
            "#0072B2" if value > 0 else
            "#D55E00" if value < 0 else "#7A7A7A"
            for value in values
        ],
        hovertemplate="%{y}<br>%{x:+,.2f} " + currency + "<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False,
        height=max(370, len(impacts) * 47 + 95),
        margin=dict(l=8, r=18, t=25, b=50),
        xaxis=dict(
            title=translate("sens_axis", currency=currency),
            zeroline=True, zerolinecolor="#6B7280", zerolinewidth=1.2,
        ),
        yaxis=dict(autorange="reversed", automargin=True),
    )
    return fig
