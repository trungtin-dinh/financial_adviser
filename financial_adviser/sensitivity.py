"""Transparent, one-at-a-time sensitivity analysis for financial assumptions.

Each test modifies one input of the *same-horizon* reference plan. It is a
conditional finite-difference experiment, not attribution, causal inference,
a probability, or a ranking of inherently important parameters.

Monthly amounts are tested at +10%; annual rates at +1 percentage point.
Zero-value amount inputs are omitted rather than claimed to have no influence.
For a rate at its allowed upper bound, the rate is reduced by 1 pp instead.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite

import pandas as pd

from .comparisons import minimum_comparison_years
from .engine import project
from .models import Plan


AMOUNT_FIELDS = (
    "monthly_income",
    "monthly_expenses",
    "monthly_investment",
)
RATE_FIELDS = (
    "income_growth_pct",
    "expense_growth_pct",
    "investment_return_pct",
    "cash_return_pct",
    "inflation_pct",
)
OPTIONAL_RATE_FIELDS = ("loan_apr_pct",)
ALL_FIELDS = AMOUNT_FIELDS + RATE_FIELDS + OPTIONAL_RATE_FIELDS


@dataclass(frozen=True)
class AssumptionImpact:
    """One test against the common reference, in scenario currency."""

    field: str
    kind: str
    baseline_value: float
    tested_value: float
    change_size: float
    final_nominal_change: float
    final_real_change: float
    minimum_cash_change: float


@dataclass(frozen=True)
class SensitivityReport:
    years: int
    baseline_final_nominal: float
    baseline_final_real: float
    baseline_minimum_cash: float
    impacts: tuple[AssumptionImpact, ...]


def analyze_assumptions(
    plan: Plan, years: int, *,
    amount_change_pct: float = 10.0,
    rate_change_pp: float = 1.0,
) -> SensitivityReport:
    """Run independent finite differences without mutating the saved plan.

    All results are calculated against a single baseline of the selected
    duration. The magnitudes of changes are deliberately displayed because
    10% of a cash amount and 1 percentage point of a rate are not directly
    comparable. This is not a standardized sensitivity ranking.
    """
    plan.validate()
    if (not isinstance(years, int) or isinstance(years, bool)
            or not minimum_comparison_years(plan) <= years <= 60):
        raise ValueError("Invalid sensitivity horizon")
    if (not isfinite(amount_change_pct) or
            not 0 < amount_change_pct <= 100):
        raise ValueError("Invalid amount perturbation")
    if (not isfinite(rate_change_pp) or
            not 0 < rate_change_pp <= 10):
        raise ValueError("Invalid rate perturbation")

    reference = replace(plan, years=years)
    reference.validate()
    baseline = project(reference)
    final_nominal = float(baseline.net_worth.iloc[-1])
    final_real = float(baseline.net_worth_real.iloc[-1])
    minimum_cash = float(baseline.cash.min())
    outputs: list[AssumptionImpact] = []
    fields = AMOUNT_FIELDS + RATE_FIELDS
    if reference.loan_balance > 0:
        fields += OPTIONAL_RATE_FIELDS

    for field in fields:
        before = float(getattr(reference, field))
        if field in AMOUNT_FIELDS:
            if before == 0.0:
                continue  # No meaningful percentage perturbation of zero.
            after = before * (1 + amount_change_pct / 100.0)
            kind = "amount"
            size = amount_change_pct
        else:
            max_rate = 100.0 if field == "loan_apr_pct" else 200.0
            step = rate_change_pp if before + rate_change_pp <= max_rate else -rate_change_pp
            after = before + step
            kind = "rate"
            size = step
        if not isfinite(after):
            raise ValueError("Non-finite tested input")
        variant = replace(reference, **{field: after})
        variant.validate()
        projection = project(variant)
        outputs.append(AssumptionImpact(
            field=field,
            kind=kind,
            baseline_value=before,
            tested_value=after,
            change_size=size,
            final_nominal_change=float(projection.net_worth.iloc[-1]) - final_nominal,
            final_real_change=float(projection.net_worth_real.iloc[-1]) - final_real,
            minimum_cash_change=float(projection.cash.min()) - minimum_cash,
        ))
    return SensitivityReport(
        years=years,
        baseline_final_nominal=final_nominal,
        baseline_final_real=final_real,
        baseline_minimum_cash=minimum_cash,
        impacts=tuple(outputs),
    )
