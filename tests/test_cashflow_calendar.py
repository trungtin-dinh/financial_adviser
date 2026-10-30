"""Regression checks for the read-only monthly cash-flow calendar."""
from dataclasses import replace

import numpy as np
import pytest

from financial_adviser.cashflow import monthly_cashflow_calendar
from financial_adviser.engine import project
from financial_adviser.models import LifeEvent, OneOff, Plan


def simple_plan(**updates):
    plan = Plan(
        years=1, initial_cash=1000, initial_investments=200,
        monthly_income=2000, monthly_expenses=1000,
        monthly_investment=300, cash_return_pct=0, investment_return_pct=0,
        income_growth_pct=0, expense_growth_pct=0,
        inflation_pct=0, loan_balance=0, goal=0,
    )
    return replace(plan, **updates)


def test_monthly_cashflow_and_internal_transfer_do_not_create_wealth():
    plan = simple_plan()
    original = project(plan)
    snapshot = original.copy(deep=True)
    calendar = monthly_cashflow_calendar(plan, original)
    assert len(calendar) == 12
    assert calendar["period"].iloc[0] == f"{plan.start_year}-01"
    assert calendar["period"].iloc[-1] == f"{plan.start_year}-12"
    assert np.allclose(calendar["investment_transfer"], -300)
    assert np.allclose(calendar["net_cashflow_before_returns"], 700)
    assert np.allclose(
        calendar["cash"].to_numpy() - original["cash"].iloc[:-1].to_numpy(),
        calendar["net_cashflow_before_returns"].to_numpy(),
    )
    assert original["net_worth"].iloc[-1] == pytest.approx(1200 + 12 * 1000)
    assert original.equals(snapshot)


def test_oneoff_and_life_event_flow_matches_projected_drivers():
    plan = simple_plan(
        one_offs=(OneOff(3, -500), OneOff(4, 100)),
        life_events=(LifeEvent("other", "Repair", 5, 2,
                               monthly_expense=200,
                               monthly_income_change=50, upfront_cost=100),),
    )
    projected = project(plan)
    calendar = monthly_cashflow_calendar(plan, projected)
    assert calendar.loc[calendar.month == 3, "one_off"].item() == -500
    assert calendar.loc[calendar.month == 4, "one_off"].item() == 100
    assert calendar.loc[calendar.month == 5, "one_off"].item() == -100
    assert calendar.loc[calendar.month == 5, "net_cashflow_before_returns"].item() == pytest.approx(450)
    assert calendar.loc[calendar.month == 6, "net_cashflow_before_returns"].item() == pytest.approx(550)


def test_projection_horizon_and_missing_fields_are_checked():
    plan = simple_plan()
    projection = project(plan)
    with pytest.raises(ValueError, match="horizon"):
        monthly_cashflow_calendar(plan, projection.iloc[:-1])
    with pytest.raises(ValueError, match="Missing"):
        monthly_cashflow_calendar(plan, projection.drop(columns=["one_off"]))


def test_cashflow_calendar_keeps_vnd_values_and_year_boundaries():
    plan = simple_plan(
        country="VN", currency="VND", years=2, start_year=2030,
        monthly_income=50_000_000, monthly_expenses=30_000_000,
        monthly_investment=10_000_000,
    )
    calendar = monthly_cashflow_calendar(plan, project(plan))
    assert calendar["period"].iloc[11] == "2030-12"
    assert calendar["period"].iloc[12] == "2031-01"
    assert calendar["net_cashflow_before_returns"].iloc[0] == pytest.approx(10_000_000)
    assert calendar.groupby("year").size().to_dict() == {2030: 12, 2031: 12}
