"""Recurring-payment regression tests: dates, conservation, compatibility, UX."""
from dataclasses import replace
import json

import numpy as np
import pytest

from financial_adviser.cashflow import monthly_cashflow_calendar
from financial_adviser.comparisons import build_comparisons, minimum_comparison_years
from financial_adviser.engine import monte_carlo, project, solve_goal
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import OneOff, Plan, RecurringFlow
from financial_adviser.planning_recurring_ui import parse_recurring_rows
from financial_adviser.ui_i18n import t


def base(**kwargs):
    return replace(Plan(
        years=2, initial_cash=10000, initial_investments=1000,
        monthly_income=0, monthly_expenses=0, monthly_investment=0,
        cash_return_pct=0, investment_return_pct=0, inflation_pct=0,
        income_growth_pct=0, expense_growth_pct=0,
        loan_balance=0, goal=0,
    ), **kwargs)


def test_monthly_quarterly_yearly_exactly_on_due_months():
    plan = base(recurring_flows=(
        RecurringFlow(1, 2, 1, -20, "Monthly"),
        RecurringFlow(2, 14, 3, -100, "Quarterly"),
        RecurringFlow(1, 24, 12, 50, "Annual"),
    ))
    df = project(plan)
    expected = np.zeros(25)
    expected[[1, 2]] -= 20
    expected[[2, 5, 8, 11, 14]] -= 100
    expected[[1, 13]] += 50
    np.testing.assert_allclose(df.recurring_flow.to_numpy(), expected)
    assert df.net_worth.iloc[-1] == pytest.approx(11000 + expected.sum())
    cal = monthly_cashflow_calendar(plan, df)
    np.testing.assert_allclose(cal.recurring_flow.to_numpy(), expected[1:])
    np.testing.assert_allclose(
        cal.net_cashflow_before_returns.to_numpy(), expected[1:]
    )
    assert cal.period.iloc[11] == "2026-12"
    assert cal.period.iloc[12] == "2027-01"


def test_recurring_flows_are_separate_from_one_offs_and_internal_transfers():
    plan = base(monthly_investment=100, initial_cash=5000,
        one_offs=(OneOff(2, -30, "Exceptional"),),
        recurring_flows=(RecurringFlow(2, 4, 1, -70, "Payment"),))
    df = project(plan)
    assert df.one_off.iloc[2] == -30
    assert df.recurring_flow.iloc[2] == -70
    assert df.one_off.iloc[3] == 0
    assert df.net_worth.iloc[-1] == pytest.approx(6000 - 30 - 210)
    cal = monthly_cashflow_calendar(plan, df)
    assert cal.investment_transfer.iloc[1] == -100
    assert cal.net_cashflow_before_returns.iloc[1] == -200
    np.testing.assert_allclose(df.cash + df.investments - df.loan_balance, df.net_worth)


def test_monte_carlo_zero_volatility_agrees_with_deterministic_schedule():
    plan = base(initial_investments=2000, monthly_investment=300,
        monthly_income=500, investment_return_pct=7, investment_volatility_pct=0,
        recurring_flows=(RecurringFlow(2, 24, 3, -400, "Quarterly"),))
    deterministic = project(plan)
    mc = monte_carlo(plan, n_paths=250, seed=7)
    assert mc.p10[-1] == pytest.approx(deterministic.net_worth.iloc[-1])
    assert mc.p50[-1] == pytest.approx(deterministic.net_worth.iloc[-1])
    assert mc.p90[-1] == pytest.approx(deterministic.net_worth.iloc[-1])


def test_schedules_survive_goal_search_and_aligned_comparisons():
    plan = base(monthly_income=1500, monthly_expenses=1000,
        recurring_flows=(RecurringFlow(6, 18, 3, -500, "Charge"),))
    assert minimum_comparison_years(plan) == 2
    with pytest.raises(ValueError, match="obligation"):
        build_comparisons(plan, 1, 2.0)
    results = solve_goal(plan, target=30000)
    assert any(v.feasible for v in results)


def test_legacy_scenarios_import_without_recurring_data():
    plan = base()
    payload = json.loads(dump_plan(plan))
    payload["plan"].pop("recurring_flows")
    assert load_plan(json.dumps(payload)).recurring_flows == ()


def test_new_scenarios_round_trip_without_changing_schema_version():
    plan = base(country="VN", currency="VND",
        initial_cash=50_000_000,
        recurring_flows=(RecurringFlow(12, 24, 12, -2_000_000, "Annual"),))
    decoded = load_plan(dump_plan(plan))
    assert decoded == plan
    assert decoded.recurring_flows[0].amount == -2_000_000


@pytest.mark.parametrize("flow", [
    RecurringFlow(0, 12, 1, 10),
    RecurringFlow(3, 2, 1, 10),
    RecurringFlow(1, 25, 12, 10),
    RecurringFlow(1, 12, 2, 10),
    RecurringFlow(1.5, 12, 1, 10),
    RecurringFlow(True, 12, 1, 10),
    RecurringFlow(1, 12, 1, float("nan")),
    RecurringFlow(1, 12, 1, 10, "x" * 121),
])
def test_invalid_recurring_flow_rejected(flow):
    with pytest.raises(ValueError):
        project(base(recurring_flows=(flow,)))


def test_entry_limit_and_parser_reject_fractional_months_and_missing_fields():
    with pytest.raises(ValueError):
        base(recurring_flows=(RecurringFlow(1, 2, 1, 10),) * 101).validate()
    with pytest.raises(ValueError):
        parse_recurring_rows([dict(start_month=2.5, end_month=12,
            frequency="monthly", amount=10)])
    with pytest.raises(ValueError):
        parse_recurring_rows([dict(start_month=1, end_month=12,
            frequency="unknown", amount=10)])
    assert parse_recurring_rows([]) == ()


def test_default_planner_and_event_template_do_not_crash():
    """Exercise the new editor and an existing event preset in the same page."""
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    planner = Path(__file__).resolve().parents[1] / "pages" / "planning.py"
    app = AppTest.from_file(str(planner), default_timeout=40)
    app.session_state["language_choice"] = "fr"
    app.run()
    assert not app.exception, app.exception
    app.selectbox(key="preset_selected").set_value("relocation").run()
    assert not app.exception, app.exception


def test_ui_schedule_translations_exist_for_every_language():
    keys = ("recurring_title", "recurring_intro", "recurring_conventions",
            "recurring_start", "recurring_end", "recurring_frequency",
            "recurring_amount", "recurring_description",
            "recurring_invalid", "cashflow_recurring",
            "recurring_monthly", "recurring_quarterly", "recurring_yearly")
    for lang in ("fr", "en", "vi"):
        assert all(t(lang, key).strip() for key in keys)
