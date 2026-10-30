"""Read-only monthly cash-flow calendar from an already calculated projection.

These flows are nominal cash movements *before* returns, and deliberately
exclude any imagined borrowing or liquidation of investments. This module
does not rerun the financial simulation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .models import Plan


def monthly_cashflow_calendar(plan: Plan, projection: pd.DataFrame) -> pd.DataFrame:
    """Return traceable month-by-month cash flows without modifying the source.

    The investment contribution is an internal transfer out of cash, not an
    expense reducing net worth. Cash balances are the engine's actual balances
    *after* its monthly cash return and may differ from these pre-return flows.
    """
    required = (
        "month", "income", "expenses", "loan_payment", "one_off", "cash",
    )
    if not set(required).issubset(projection.columns):
        raise ValueError("Missing cash-flow projection fields")
    months = np.arange(plan.years * 12 + 1)
    if len(projection) != len(months) or not np.array_equal(
        projection["month"].to_numpy(), months
    ):
        raise ValueError("Projection does not match the saved plan horizon")
    if not np.isfinite(projection[list(required)].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite projection values")

    source = projection.iloc[1:]
    month = source["month"].to_numpy(dtype=int)
    year = plan.start_year + (month - 1) // 12
    calendar_month = (month - 1) % 12 + 1
    income = source["income"].to_numpy(dtype=float)
    expenses = source["expenses"].to_numpy(dtype=float)
    loan = source["loan_payment"].to_numpy(dtype=float)
    events = source["one_off"].to_numpy(dtype=float)
    transfers = np.full(len(month), -plan.monthly_investment)
    before_returns = income - expenses - loan + events + transfers

    return pd.DataFrame({
        "month": month,
        "year": year,
        "period": [f"{y:04d}-{m:02d}" for y, m in zip(year, calendar_month)],
        "income": income,
        "expenses": expenses,
        "loan_payment": loan,
        "one_off": events,
        "investment_transfer": transfers,
        "net_cashflow_before_returns": before_returns,
        "cash": source["cash"].to_numpy(dtype=float),
    })
