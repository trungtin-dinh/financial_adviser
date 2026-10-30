"""Compare two independently configured financial plans on a common horizon.

Both scenarios retain their own cash, investments, household and life events.
Comparison never mutates either Plan. A common country, currency, start year
and nominal target are necessary for meaningful side-by-side results.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

import pandas as pd

from .comparisons import minimum_comparison_years
from .engine import project
from .models import Plan


# Editable fields in the on-screen copy-of-reference workflow. More complex
# events/households can be introduced by importing an existing full plan JSON.
CUSTOM_AMOUNT_FIELDS = (
    "initial_cash", "initial_investments", "monthly_income",
    "monthly_expenses", "monthly_investment", "loan_balance",
    "initial_property_value", "initial_other_assets",
)
CUSTOM_RATE_FIELDS = (
    "income_growth_pct", "expense_growth_pct", "cash_return_pct",
    "investment_return_pct", "inflation_pct", "loan_apr_pct",
    "property_growth_pct",
)
CUSTOM_INTEGER_FIELDS = ("loan_years",)
CUSTOM_FIELDS = CUSTOM_AMOUNT_FIELDS + CUSTOM_RATE_FIELDS + CUSTOM_INTEGER_FIELDS


@dataclass(frozen=True)
class ScenarioComparison:
    reference_plan: Plan
    alternative_plan: Plan
    years: int
    reference: pd.DataFrame
    alternative: pd.DataFrame
    nominal_difference: float
    real_difference: float
    minimum_cash_difference: float
    reference_deficit_months: int
    alternative_deficit_months: int
    reference_funding_gap: float
    alternative_funding_gap: float
    reference_goal_reached: bool | None
    alternative_goal_reached: bool | None


def make_custom_variant(base: Plan, changes: dict[str, float | int]) -> Plan:
    """Edit multiple *explicitly allowlisted* input fields on a copied plan."""
    base.validate()
    if not isinstance(changes, dict) or set(changes) - set(CUSTOM_FIELDS):
        raise ValueError("Unsupported customized assumption")
    valid: dict[str, float | int] = {}
    for field, value in changes.items():
        if field in CUSTOM_INTEGER_FIELDS:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("Loan duration must be an integer")
            valid[field] = value
        elif isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("Customized amount or rate must be finite")
        else:
            valid[field] = float(value)
    variant = replace(base, **valid)
    variant.validate()
    return variant


def compare_custom_scenarios(
    reference: Plan, alternative: Plan, years: int,
) -> ScenarioComparison:
    """Compare two scenarios at the same local dates and nominal target.

    The entered plan's years may differ; the selected comparison horizon is
    applied to both only after validating their dated obligations. No future
    event is silently dropped. Debt and liquid assets are NOT combined across
    scenarios. Returns and inflation remain conditional assumptions.
    """
    reference.validate()
    alternative.validate()
    if reference.country != alternative.country:
        raise ValueError("Different scenario countries")
    if reference.currency != alternative.currency:
        raise ValueError("Different scenario currencies")
    if reference.start_year != alternative.start_year:
        raise ValueError("Different scenario start years")
    if reference.goal != alternative.goal:
        raise ValueError("Different nominal wealth targets")
    if isinstance(years, bool) or not isinstance(years, int) or not 1 <= years <= 60:
        raise ValueError("Invalid common comparison horizon")
    if years < max(minimum_comparison_years(reference),
                   minimum_comparison_years(alternative)):
        raise ValueError("Comparison horizon excludes dated obligations")

    left_plan = replace(reference, years=years)
    right_plan = replace(alternative, years=years)
    left_plan.validate()
    right_plan.validate()
    left = project(left_plan)
    right = project(right_plan)
    if not left.month.equals(right.month):
        raise ValueError("Comparison date grids do not match")

    left_end = left.iloc[-1]
    right_end = right.iloc[-1]
    target = reference.goal
    lmin, rmin = float(left.cash.min()), float(right.cash.min())
    return ScenarioComparison(
        reference_plan=left_plan,
        alternative_plan=right_plan,
        years=years,
        reference=left,
        alternative=right,
        nominal_difference=float(right_end.net_worth - left_end.net_worth),
        real_difference=float(right_end.net_worth_real - left_end.net_worth_real),
        minimum_cash_difference=rmin - lmin,
        reference_deficit_months=int((left.cash.iloc[1:] < 0).sum()),
        alternative_deficit_months=int((right.cash.iloc[1:] < 0).sum()),
        reference_funding_gap=max(0.0, -lmin),
        alternative_funding_gap=max(0.0, -rmin),
        reference_goal_reached=bool(left_end.net_worth >= target)
                               if target > 0 else None,
        alternative_goal_reached=bool(right_end.net_worth >= target)
                                 if target > 0 else None,
    )
