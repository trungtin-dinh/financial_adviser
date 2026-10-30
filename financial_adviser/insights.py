"""Explain an existing financial projection with descriptive, auditable facts.

No arbitrary risk score, investment recommendation or statistical probability
is assigned. These values come exclusively from the saved deterministic
projection, not from edited-but-not-yet-recomputed form inputs.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .models import Plan


@dataclass(frozen=True)
class FinancialOverview:
    """Small set of facts suitable for a multilingual public results summary."""

    first_month_regular_balance: float
    first_deficit_month: int | None
    negative_cash_months: int
    funding_gap: float
    final_nominal_wealth: float
    final_real_wealth: float
    goal_is_specified: bool
    nominal_goal_reached: bool
    nominal_goal_gap: float
    inflation_pct: float


def summarize_projection(plan: Plan, projection: pd.DataFrame) -> FinancialOverview:
    """Read the actual simulated monthly amounts, without recalculating the plan.

    The first-month operating balance is the actual modeled monthly income
    minus expenses, the month's loan installment and the internal transfer to
    investments. It intentionally excludes one-off flows and interest returns.
    This is a one-month snapshot, NOT an average or a multi-year forecast.

    A goal is nominal and checked only at the end of the projection. It does
    not certify that the path stayed liquid; this is tracked independently.
    The inflation-adjusted final wealth is reported, never compared directly
    to the nominal target.
    """
    plan.validate()
    required = {
        "month", "cash", "income", "expenses", "loan_payment",
        "net_worth", "net_worth_real",
    }
    if not required.issubset(projection.columns):
        raise ValueError("Missing financial projection fields")
    expected_months = np.arange(plan.years * 12 + 1)
    if (len(projection) != len(expected_months)
            or not np.array_equal(projection["month"].to_numpy(), expected_months)):
        raise ValueError("Projection does not match the saved plan horizon")

    values = projection[list(required)].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Non-finite projection values")

    first = projection.iloc[1]
    final = projection.iloc[-1]
    cash = projection["cash"].to_numpy(dtype=float)
    negative = np.flatnonzero(cash[1:] < 0.0)
    first_deficit = int(negative[0] + 1) if negative.size else None
    first_month_balance = float(
        first["income"] - first["expenses"] - first["loan_payment"]
        - plan.monthly_investment
    )
    nominal_final = float(final["net_worth"])
    goal_specified = plan.goal > 0
    return FinancialOverview(
        first_month_regular_balance=first_month_balance,
        first_deficit_month=first_deficit,
        negative_cash_months=int(negative.size),
        funding_gap=max(0.0, -float(np.min(cash))),
        final_nominal_wealth=nominal_final,
        final_real_wealth=float(final["net_worth_real"]),
        goal_is_specified=goal_specified,
        nominal_goal_reached=bool(goal_specified and nominal_final >= plan.goal),
        nominal_goal_gap=max(0.0, plan.goal - nominal_final)
                         if goal_specified else 0.0,
        inflation_pct=float(plan.inflation_pct),
    )
