"""Liquidity resilience measures for an educational financial projection.

No probabilistic rating or recommended emergency-fund threshold is inferred.
Only cash is treated as immediately available: investments are never sold
implicitly, credit is never created, and the saved financial plan is unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np
import pandas as pd

from .engine import loan_payment, monthly_rate
from .models import Plan


@dataclass(frozen=True)
class LiquidityResilience:
    """Descriptive baseline and hypothetical one-off shock diagnostics."""

    initial_monthly_outflows: float
    static_reserve_months: float | None
    baseline_first_deficit_month: int | None
    baseline_deficit_months: int
    baseline_minimum_cash: float
    baseline_funding_gap: float
    shock_month: int
    shock_amount: float
    maximum_absorbable_expense: float
    shock_first_deficit_month: int | None
    shock_deficit_months: int
    shock_minimum_cash: float
    shock_funding_gap: float
    baseline_cash: np.ndarray
    stressed_cash: np.ndarray


def _deficits(cash: np.ndarray) -> tuple[int | None, int, float, float]:
    """The initial position is not a projected month."""
    negative = np.flatnonzero(cash[1:] < 0.0)
    minimum = float(np.min(cash))
    return (
        int(negative[0] + 1) if negative.size else None,
        int(negative.size),
        minimum,
        max(0.0, -minimum),
    )


def analyze_liquidity(
    plan: Plan, projected: pd.DataFrame,
    *, shock_month: int = 1, shock_amount: float = 0.0,
) -> LiquidityResilience:
    """Evaluate a hypothetical expense without recomputing the whole plan.

    The engine's cash recurrence is C[m] = (C[m-1] + net_flow[m]) * g,
    where g = (1 + annual_cash_return) ** (1 / 12).
    A one-time expense A at the START of projected month k therefore reduces
    C[m] by A * g ** (m-k+1) for m >= k.

    If the original cash trajectory never goes negative, the largest expense
    that can be absorbed at month k without a negative balance through the
    END of the projection is min(C[m] / g ** (m-k+1), for m >= k).
    An existing baseline deficit implies no such full-horizon guarantee.
    This is a mathematical cash-only capacity, not financial advice.
    """
    plan.validate()
    n = plan.years * 12
    if (not isinstance(shock_month, int) or isinstance(shock_month, bool)
            or not 1 <= shock_month <= n):
        raise ValueError("Invalid expense month")
    if (not isinstance(shock_amount, (int, float))
            or not isfinite(shock_amount) or shock_amount < 0):
        raise ValueError("The extra expense must be finite and nonnegative")
    if (len(projected) != n + 1
            or not {"month", "cash"}.issubset(projected.columns)):
        raise ValueError("The projection does not match the plan horizon")
    if not np.array_equal(
            projected["month"].to_numpy(), np.arange(n + 1)):
        raise ValueError("Unexpected projection month grid")
    baseline = projected["cash"].to_numpy(dtype=float, copy=True)
    if not np.isfinite(baseline).all():
        raise ValueError("Non-finite cash in the original projection")

    repayment = loan_payment(plan.loan_balance, plan.loan_apr_pct, plan.loan_years)
    initial_outflows = float(plan.monthly_expenses + repayment)
    reserve = (float(plan.initial_cash / initial_outflows)
               if initial_outflows > 0 else None)

    growth = 1.0 + monthly_rate(plan.cash_return_pct)
    periods = np.arange(1, n - shock_month + 2, dtype=float)
    factors = np.power(growth, periods)
    if not np.isfinite(factors).all() or (factors <= 0).any():
        raise ValueError("Invalid cash return assumptions")

    baseline_first, baseline_months, baseline_min, baseline_gap = _deficits(baseline)
    if baseline_min < 0:
        capacity = 0.0
    else:
        capacity = max(0.0, float(np.min(baseline[shock_month:] / factors)))

    stressed = baseline.copy()
    stressed[shock_month:] -= float(shock_amount) * factors
    if not np.isfinite(stressed).all():
        raise ValueError("The selected expense is too large to simulate")
    stress_first, stress_months, stress_min, stress_gap = _deficits(stressed)
    return LiquidityResilience(
        initial_monthly_outflows=initial_outflows,
        static_reserve_months=reserve,
        baseline_first_deficit_month=baseline_first,
        baseline_deficit_months=baseline_months,
        baseline_minimum_cash=baseline_min,
        baseline_funding_gap=baseline_gap,
        shock_month=shock_month,
        shock_amount=float(shock_amount),
        maximum_absorbable_expense=capacity,
        shock_first_deficit_month=stress_first,
        shock_deficit_months=stress_months,
        shock_minimum_cash=stress_min,
        shock_funding_gap=stress_gap,
        baseline_cash=baseline,
        stressed_cash=stressed,
    )
