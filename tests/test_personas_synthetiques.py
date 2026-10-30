"""Synthetic socioeconomic scenarios, not peer review by actual human participants."""
from dataclasses import replace

import pytest

from financial_adviser.engine import project, solve_goal
from financial_adviser.models import Plan, LifeEvent


def neutral(**overrides):
    baseline = Plan(years=2, initial_cash=10_000, initial_investments=0,
        monthly_income=2_000, monthly_expenses=1_600, monthly_investment=0,
        cash_return_pct=0, investment_return_pct=0, inflation_pct=0,
        income_growth_pct=0, expense_growth_pct=0, loan_balance=0)
    return replace(baseline, **overrides)


@pytest.mark.parametrize("profile,event,impact", [
    ("single_parent", LifeEvent("child", "care", 3, 12, monthly_expense=300), -3600),
    ("illness", LifeEvent("health", "care", 1, 2, monthly_expense=400, monthly_income_change=-600), -2000),
    ("unemployment", LifeEvent("unemployment", "no work", 7, 3, monthly_income_change=-2000), -6000),
    ("major_purchase", LifeEvent("purchase", "vehicle", 6, 1, upfront_cost=4000), -4000),
    ("older_relative", LifeEvent("health", "long-term care", 1, 24, monthly_expense=250), -6000),
    ("relocation", LifeEvent("relocation", "move", 4, 1, upfront_cost=1250), -1250),
])
def test_synthetic_event_impact(profile, event, impact):
    base = neutral()
    without = project(base)
    with_event = project(replace(base, life_events=(event,)))
    assert with_event.net_worth.iloc[-1] - without.net_worth.iloc[-1] == pytest.approx(impact)


def test_cash_shortage_visible_for_low_income_student_profile():
    plan = neutral(initial_cash=0, monthly_income=800, monthly_expenses=1250)
    assert project(plan).cash.min() < 0


def test_vietnam_synthetic_scenario_retains_currency_without_conversion():
    plan = neutral(country="VN", currency="VND", initial_cash=10_000_000,
                   monthly_income=30_000_000, monthly_expenses=20_000_000)
    output = project(plan)
    assert output.cash.iloc[0] == 10_000_000
    assert output.cash.iloc[-1] == pytest.approx(10_000_000 + 24 * 10_000_000)


def test_event_cost_and_income_change_are_additive_for_flat_zero_rate_model():
    first = LifeEvent("child", "support", 1, 4, monthly_expense=100)
    second = LifeEvent("health", "care", 3, 2, monthly_income_change=-500, upfront_cost=300)
    base = neutral()
    with_both = project(replace(base, life_events=(first, second)))
    without = project(base)
    assert with_both.net_worth.iloc[-1] - without.net_worth.iloc[-1] == pytest.approx(-1700)


def test_inverse_goal_does_not_claim_a_hypothetical_spending_reduction_is_feasible():
    base = neutral(monthly_income=0, monthly_expenses=0, initial_cash=0, goal=50_000)
    solutions = solve_goal(base, target=50_000)
    spending = next(s for s in solutions if s.lever == "expenses")
    assert not spending.feasible
