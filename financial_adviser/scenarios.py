"""Transparent, editable, deterministic life-event templates and stress testing.

Templates are explicitly illustrative, not estimates of real-world incidence or
national typical costs. They are NOT attached to a plan unless confirmed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

import numpy as np
import pandas as pd

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


@dataclass(frozen=True)
class StressEvaluation:
    """Observed consequences of one deterministic stress on a saved scenario.

    These figures are *conditional scenario outputs*, never occurrence
    probabilities. A negative simulated cash balance is an unfunded need.
    """
    impact: StressImpact
    baseline: pd.DataFrame
    stressed: pd.DataFrame
    first_deficit_month: int | None
    deficit_months: int
    newly_negative_months: int
    peak_funding_need: float
    baseline_funding_need: float


def evaluate_stresses(
    plan: Plan,
    keys: tuple[str, ...],
    first_month: int = 1,
) -> tuple[StressEvaluation, ...]:
    """Compare independent shocks against the same deterministic reference.

    All input shocks begin at first_month; their illustrative durations are
    clipped to the remaining horizon. Base life events are preserved. A single
    baseline is calculated per evaluation, avoiding one redundant reference
    projection for every selected shock.
    """
    from .engine import project

    plan.validate()
    if not isinstance(first_month, int) or isinstance(first_month, bool):
        raise ValueError("Stress start month must be an integer")
    if not 1 <= first_month <= plan.years * 12:
        raise ValueError("Stress start month outside projection")
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate stress templates are not allowed")
    if any(key not in PRESET_IDS for key in keys):
        raise ValueError("Unknown stress scenario")
    if not keys:
        return ()

    baseline = project(plan)
    baseline_cash = baseline.cash.to_numpy(dtype=float)
    baseline_negative = baseline_cash[1:] < 0
    baseline_gap = max(0.0, -float(baseline_cash.min()))
    results: list[StressEvaluation] = []
    for key in keys:
        event = proposed_event(plan, key, first_month=first_month)
        stress_plan = replace(plan, life_events=plan.life_events + (event,))
        stressed = project(stress_plan)
        stressed_cash = stressed.cash.to_numpy(dtype=float)
        negative = stressed_cash[1:] < 0
        negative_positions = np.flatnonzero(negative)
        first_negative = int(negative_positions[0] + 1) if negative_positions.size else None
        terminal_delta = float(stressed.net_worth.iloc[-1] - baseline.net_worth.iloc[-1])
        lowest_cash = float(stressed_cash.min())
        lowest_cash_delta = lowest_cash - float(baseline_cash.min())
        if not all(isfinite(x) for x in (terminal_delta, lowest_cash, lowest_cash_delta)):
            raise ValueError("Stress scenario produced non-finite values")
        impact = StressImpact(
            key=key,
            event=event,
            terminal_delta=terminal_delta,
            lowest_cash=lowest_cash,
            lowest_cash_delta=lowest_cash_delta,
            liquidity_breach=bool(negative.any()),
        )
        results.append(StressEvaluation(
            impact=impact,
            baseline=baseline,
            stressed=stressed,
            first_deficit_month=first_negative,
            deficit_months=int(negative.sum()),
            newly_negative_months=int((negative & ~baseline_negative).sum()),
            peak_funding_need=max(0.0, -lowest_cash),
            baseline_funding_need=baseline_gap,
        ))
    return tuple(results)


def stress_impact(plan: Plan, key: str, first_month: int = 1) -> StressImpact:
    """Compatibility API: one deterministic shock versus the same baseline."""
    return evaluate_stresses(plan, (key,), first_month=first_month)[0].impact
