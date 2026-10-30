"""Regression tests for cash reserve and conditional expense absorption.

The shock calculation is checked against an independently rerun full monthly
projection, including investment transfers, cash returns and household events.
"""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import resilience_figure
from financial_adviser.engine import project, loan_payment
from financial_adviser.models import LifeEvent, OneOff, Plan
from financial_adviser.resilience import analyze_liquidity
from financial_adviser.ui_i18n import t


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("annual_return", [-25.0, 0.0, 1.5, 30.0])
@pytest.mark.parametrize("shock_month", [1, 6, 24])
def test_extra_expense_matches_full_financial_projection(annual_return, shock_month):
    plan = Plan(
        years=2, initial_cash=30_000, initial_investments=5_000,
        monthly_income=3_200, monthly_expenses=2_200,
        monthly_investment=420, loan_balance=14_000, loan_apr_pct=3.8,
        loan_years=3, cash_return_pct=annual_return,
        one_offs=(OneOff(4, 350, "Bonus"),),
        life_events=(LifeEvent("relocation", "Move", 8, 2,
                               monthly_expense=120, upfront_cost=300),),
    )
    original = project(plan)
    shock = 750.0
    measured = analyze_liquidity(
        plan, original, shock_month=shock_month, shock_amount=shock)
    rerun = project(replace(
        plan, one_offs=plan.one_offs + (OneOff(shock_month, -shock, "Shock"),)))
    np.testing.assert_allclose(measured.stressed_cash, rerun.cash, atol=1e-6)
    np.testing.assert_allclose(measured.baseline_cash, original.cash, atol=0)
    assert measured.static_reserve_months == pytest.approx(
        plan.initial_cash / (plan.monthly_expenses +
                             loan_payment(plan.loan_balance, plan.loan_apr_pct, plan.loan_years)))
    assert measured.shock_funding_gap == pytest.approx(
        max(0.0, -float(rerun.cash.min())))
    assert measured.baseline_funding_gap == pytest.approx(
        max(0.0, -float(original.cash.min())))
    assert plan.one_offs == (OneOff(4, 350, "Bonus"),)


def test_capacity_is_largest_outflow_without_any_future_negative_cash():
    plan = Plan(
        years=2, initial_cash=7_000, monthly_income=1_500,
        monthly_expenses=1_300, monthly_investment=100,
        cash_return_pct=1.2, investment_return_pct=0,
    )
    df = project(plan)
    for month in (1, 10, 24):
        base = analyze_liquidity(plan, df, shock_month=month)
        assert base.baseline_funding_gap == 0
        assert base.maximum_absorbable_expense > 0
        affordable = analyze_liquidity(
            plan, df, shock_month=month,
            shock_amount=0.9999 * base.maximum_absorbable_expense)
        excessive = analyze_liquidity(
            plan, df, shock_month=month,
            shock_amount=1.0001 * base.maximum_absorbable_expense)
        assert affordable.shock_first_deficit_month is None
        assert excessive.shock_first_deficit_month is not None
        assert excessive.shock_funding_gap > 0


def test_preexisting_deficit_cannot_be_presented_as_shock_reserve():
    plan = Plan(
        years=1, initial_cash=0, initial_investments=100_000,
        monthly_income=0, monthly_expenses=500,
        monthly_investment=0, investment_return_pct=5.0)
    df = project(plan)
    m = analyze_liquidity(plan, df, shock_month=7, shock_amount=10)
    assert m.baseline_first_deficit_month == 1
    assert m.baseline_deficit_months == 12
    assert m.maximum_absorbable_expense == 0
    assert m.baseline_funding_gap > 0
    # Investments are *not* silently liquidated to cover monthly expenses.
    assert m.shock_funding_gap > m.baseline_funding_gap
    assert plan.initial_investments == 100_000


def test_static_buffer_no_required_outflows_is_not_applicable():
    plan = Plan(
        years=1, initial_cash=50, monthly_income=0, monthly_expenses=0,
        monthly_investment=0, loan_balance=0, cash_return_pct=0)
    m = analyze_liquidity(plan, project(plan))
    assert m.initial_monthly_outflows == 0
    assert m.static_reserve_months is None
    assert m.maximum_absorbable_expense == pytest.approx(50)
    assert m.baseline_funding_gap == 0
    assert m.shock_funding_gap == 0


@pytest.mark.parametrize("month,amount", [
    (0, 10), (13, 10), (True, 10), (1.0, 10),
    (1, -1), (1, float("inf")), (1, float("nan")),
])
def test_invalid_shock_request_rejected(month, amount):
    plan = Plan(years=1)
    with pytest.raises(ValueError):
        analyze_liquidity(
            plan, project(plan), shock_month=month, shock_amount=amount)


def test_projection_grid_mismatch_is_not_silently_accepted():
    p = Plan(years=1)
    df = project(p)
    with pytest.raises(ValueError):
        analyze_liquidity(p, df.iloc[:-1])
    shifted = df.copy()
    shifted.loc[1, "month"] = 200
    with pytest.raises(ValueError):
        analyze_liquidity(p, shifted)


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_chart_contains_cash_values_without_arbitrary_risk_score(lang):
    p = Plan(years=1, initial_cash=900, monthly_income=900,
             monthly_expenses=1_000, monthly_investment=0,
             cash_return_pct=0)
    df = project(p)
    m = analyze_liquidity(p, df, shock_month=3, shock_amount=250)
    fig = resilience_figure(
        df, m, p.start_year, p.currency, lambda k: t(lang, k))
    assert len(fig.data) == 2
    np.testing.assert_allclose(fig.data[0].y, m.baseline_cash)
    np.testing.assert_allclose(fig.data[1].y, m.stressed_cash)
    assert len(fig.layout.shapes) == 3  # zero, red deficit area, date
    assert "risk" not in str(fig.layout).lower()
    assert fig.layout.yaxis.title.text == p.currency


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_streamlit_resilience_panel_retains_saved_plan_and_results(lang):
    p = Plan(
        years=2, initial_cash=200, monthly_income=1_000,
        monthly_expenses=900, monthly_investment=0)
    df = project(p)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = lang
    app.session_state["plan"] = p
    app.session_state["result"] = {"plan": p, "df": df, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert app.number_input(key="resilience_shock_month").value == 1
    assert app.number_input(key="resilience_expense_amount").value == 0
    assert any(t(lang, "resilience_title") in ex.label
               for ex in app.get("expander"))
    app.number_input(key="resilience_shock_month").set_value(8).run()
    app.number_input(key="resilience_expense_amount").set_value(1_500.0).run()
    assert not app.exception, app.exception
    assert app.number_input(key="resilience_shock_month").value == 8
    assert any(t(lang, "resilience_test_gap") == met.label
               for met in app.get("metric"))
    assert app.session_state["plan"] == p
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
