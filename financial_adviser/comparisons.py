"""Aligned financial what-if comparisons at an explicitly selected horizon.

The same time horizon, target and base assumptions are used for every row.
This module does not contain presentation strings or user-interface state.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import ceil, isfinite

import pandas as pd

from .engine import project
from .models import Plan


@dataclass(frozen=True)
class ComparisonCase:
    key: str
    return_pct: float
    projection: pd.DataFrame
    terminal_nominal: float
    terminal_real: float
    terminal_delta: float
    minimum_cash: float
    goal_reached: bool


def minimum_comparison_years(plan: Plan) -> int:
    """The smallest horizon that preserves all explicitly dated obligations.

    Periodic budgets (e.g. child costs) are naturally truncated at the chosen
    horizon; explicit life events and dependent-support commitments must not
    silently disappear because the user shortened the comparison.
    """
    last_month = max(
        [1]
        + [e.month for e in plan.one_offs]
        + [e.first_month + e.duration_months - 1 for e in plan.life_events]
        + [person.first_month + person.duration_months - 1
           for person in plan.dependents]
        + [child.arrival_month for child in plan.children]
    )
    return max(1, ceil(last_month / 12))


def build_comparisons(
    plan: Plan, years: int, return_shock_pct: float,
) -> tuple[ComparisonCase, ...]:
    """Five (or three) mutually exclusive sensitivity scenarios.

    A comparison horizon is shared by every curve and result row. All
    terminal deltas are measured against the *same-horizon* reference case.
    Individual projections are not accumulated or assigned probabilities.
    """
    plan.validate()
    if not isinstance(years, int) or isinstance(years, bool):
        raise ValueError("Comparison horizon must be an integer")
    if not minimum_comparison_years(plan) <= years <= 60:
        raise ValueError("Comparison horizon excludes a dated obligation")
    if (not isfinite(return_shock_pct)
            or not 0.5 <= return_shock_pct <= 10):
        raise ValueError("Invalid investment return sensitivity")

    base = replace(plan, years=years)
    base.validate()
    scenarios = [
        ("scenario_lower", replace(
            base, investment_return_pct=max(
                -98.0, base.investment_return_pct - return_shock_pct))),
        ("scenario_base", base),
        ("scenario_higher", replace(
            base, investment_return_pct=min(
                200.0, base.investment_return_pct + return_shock_pct))),
    ]
    if base.life_events:
        scenarios.extend((
            ("scenario_no_events", replace(base, life_events=())),
            ("scenario_events_more", replace(base, life_events=tuple(
                replace(e, monthly_expense=e.monthly_expense * 1.25,
                        upfront_cost=e.upfront_cost * 1.25)
                for e in base.life_events
            ))),
        ))
    baseline = project(base)
    baseline_terminal = float(baseline.net_worth.iloc[-1])
    results = []
    for key, scenario in scenarios:
        projected = baseline if key == "scenario_base" else project(scenario)
        nominal = float(projected.net_worth.iloc[-1])
        results.append(ComparisonCase(
            key=key,
            return_pct=scenario.investment_return_pct,
            projection=projected,
            terminal_nominal=nominal,
            terminal_real=float(projected.net_worth_real.iloc[-1]),
            terminal_delta=nominal - baseline_terminal,
            minimum_cash=float(projected.cash.min()),
            goal_reached=nominal >= scenario.goal,
        ))
    return tuple(results)
