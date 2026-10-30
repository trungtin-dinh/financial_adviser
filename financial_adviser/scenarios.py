"""Transparent, editable, deterministic life-event templates and stress testing.

Templates are explicitly illustrative, not estimates of real-world incidence or
national typical costs. They are NOT attached to a plan unless confirmed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

from .models import LifeEvent, Plan

PRESET_IDS = ("job_gap", "health_costs", "unexpected_purchase", "child_care", "family_support", "relocation")

# IDs are stable across FR / EN / VI; localized labels only belong in the UI.
_PRESET = {
    # category, default duration, recurring expense / initial spending,
    # income difference / initial income, upfront cost / initial spending.
    "job_gap": ("unemployment", 3, 0.0, -1.0, 0.0),
    "health_costs": ("health", 2, 0.25, -0.30, 0.50),
    "unexpected_purchase": ("purchase", 1, 0.0, 0.0, 2.0),
    "child_care": ("child", 36, 0.20, 0.0, 0.50),
    "family_support": ("other", 12, 0.15, 0.0, 0.0),
    "relocation": ("relocation", 1, 0.0, 0.0, 1.5),
}


@dataclass(frozen=True)
class StressImpact:
    """Terminal impacts are nominal; lowest cash tests the whole horizon."""
    key: str
    event: LifeEvent
    terminal_delta: float
    lowest_cash: float
    lowest_cash_delta: float
    liquidity_breach: bool


def proposed_event(
    plan: Plan, key: str, first_month: int = 1,
    duration_months: int | None = None, label: str | None = None,
) -> LifeEvent:
    """Generate an editable draft using clearly hypothetical % of *this plan*.

    Duration is clipped only when using the DEFAULT duration, never silently
    when the user supplies an explicit duration; explicit invalid data fails.
    """
    plan.validate()
    if key not in _PRESET:
        raise ValueError("Unknown event template")
    if not isinstance(first_month, int) or isinstance(first_month, bool) or not 1 <= first_month <= plan.years * 12:
        raise ValueError("Start month outside the projection")
    category, default_duration, spend_frac, income_frac, upfront_frac = _PRESET[key]
    remaining = plan.years * 12 - first_month + 1
    duration = min(default_duration, remaining) if duration_months is None else duration_months
    if not isinstance(duration, int) or isinstance(duration, bool) or not 1 <= duration <= remaining:
        raise ValueError("Event duration outside projection")
    event = LifeEvent(
        category=category, label=label or key,
        first_month=first_month, duration_months=duration,
        monthly_expense=plan.monthly_expenses * spend_frac,
        monthly_income_change=plan.monthly_income * income_frac,
        upfront_cost=plan.monthly_expenses * upfront_frac,
    )
    replace(plan, life_events=plan.life_events + (event,)).validate()
    return event


def stress_impact(plan: Plan, key: str, first_month: int = 1) -> StressImpact:
    """Compare one optional shock against a baseline; never mutate the plan.

    Not probability-weighted; no stochastic risk estimation. User-defined
    life events stay in the baseline. No hidden addition to the reference case.
    """
    from .engine import project

    event = proposed_event(plan, key, first_month)
    baseline = project(plan)
    scenario = project(replace(plan, life_events=plan.life_events + (event,)))
    terminal_delta = float(scenario.net_worth.iloc[-1] - baseline.net_worth.iloc[-1])
    min_cash = float(scenario.cash.min())
    if not all(isfinite(x) for x in (terminal_delta, min_cash)):
        raise ValueError("Stress scenario produced non-finite values")
    return StressImpact(
        key=key, event=event, terminal_delta=terminal_delta,
        lowest_cash=min_cash,
        lowest_cash_delta=min_cash - float(baseline.cash.min()),
        liquidity_breach=bool((scenario.cash < 0).any()),
    )
