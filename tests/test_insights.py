"""Accuracy and UI regression checks for the explanatory results summary."""
from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.engine import loan_payment, project
from financial_adviser.charts import WEALTH_SERIES, wealth_figure, comparison_figure
from financial_adviser.comparisons import build_comparisons
from financial_adviser.insights import summarize_projection
from financial_adviser.models import LifeEvent, Plan
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def test_first_month_regular_margin_uses_actual_projected_flows():
    plan = Plan(
        years=2, initial_cash=12_000, monthly_income=3_000,
        monthly_expenses=2_000, monthly_investment=400,
        loan_balance=9_000, loan_apr_pct=3, loan_years=2,
        life_events=(LifeEvent("other", "Extra expenses", first_month=1,
                               duration_months=2, monthly_expense=100,
                               monthly_income_change=-200, upfront_cost=500),),
    )
    df = project(plan)
    snapshot = df.copy(deep=True)
    facts = summarize_projection(plan, df)
    payment = loan_payment(plan.loan_balance, plan.loan_apr_pct, plan.loan_years)
    assert facts.first_month_regular_balance == pytest.approx(
        3_000 - 200 - (2_000 + 100) - payment - 400)
    # The one-off cost of 500 is excluded from this regular monthly balance.
    assert facts.first_month_regular_balance != pytest.approx(
        3_000 - 200 - 2_100 - payment - 400 - 500)
    assert facts.inflation_pct == plan.inflation_pct
    pd.testing.assert_frame_equal(df, snapshot)


def test_liquidity_and_nominal_goal_are_independent():
    plan = Plan(
        years=1, initial_cash=0, initial_investments=150_000,
        monthly_income=0, monthly_expenses=2_000,
        monthly_investment=0, goal=1_000, cash_return_pct=0,
        investment_return_pct=5, expense_growth_pct=0,
    )
    df = project(plan)
    facts = summarize_projection(plan, df)
    assert facts.goal_is_specified
    assert facts.nominal_goal_reached  # Positive investments do not create cash.
    assert facts.first_deficit_month == 1
    assert facts.negative_cash_months == 12
    assert facts.funding_gap == pytest.approx(24_000)
    assert facts.first_month_regular_balance == pytest.approx(-2_000)
    assert plan.initial_cash == 0


def test_missing_goal_has_no_false_positive_achievement():
    plan = Plan(years=1, goal=0, initial_cash=2_000)
    facts = summarize_projection(plan, project(plan))
    assert facts.goal_is_specified is False
    assert facts.nominal_goal_reached is False
    assert facts.nominal_goal_gap == 0


def test_unreached_goal_gap_is_nominal_only():
    plan = Plan(
        years=1, goal=1_000_000, initial_cash=0,
        initial_investments=0, monthly_income=0, monthly_expenses=0,
        monthly_investment=0, inflation_pct=15,
    )
    facts = summarize_projection(plan, project(plan))
    assert facts.goal_is_specified
    assert not facts.nominal_goal_reached
    assert facts.nominal_goal_gap == pytest.approx(1_000_000)
    assert facts.first_deficit_month is None
    assert facts.first_month_regular_balance == 0


def test_deflation_does_not_get_described_as_wealth_loss():
    plan = Plan(
        years=2, inflation_pct=-3,
        initial_cash=20_000, monthly_income=1000, monthly_expenses=700,
        monthly_investment=0, initial_investments=0,
    )
    facts = summarize_projection(plan, project(plan))
    assert facts.final_real_wealth > facts.final_nominal_wealth
    assert facts.inflation_pct < 0
    assert facts.first_deficit_month is None


@pytest.mark.parametrize("alteration", ["missing", "length", "months", "nan"])
def test_invalid_or_mismatched_projection_rejected(alteration):
    plan = Plan(years=1)
    df = project(plan)
    if alteration == "missing":
        df = df.drop(columns=["loan_payment"])
    elif alteration == "length":
        df = df.iloc[:-1]
    elif alteration == "months":
        df = df.copy()
        df.loc[1, "month"] = 3
    elif alteration == "nan":
        df = df.copy()
        df.loc[2, "cash"] = float("nan")
    with pytest.raises(ValueError):
        summarize_projection(plan, df)


@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_public_summary_is_readable_and_derived_from_saved_scenario(language):
    plan = Plan(
        years=1, initial_cash=0, initial_investments=150_000,
        monthly_income=0, monthly_expenses=2_000,
        monthly_investment=0, goal=1000, cash_return_pct=0,
    )
    df = project(plan)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = plan
    app.session_state["result"] = {"plan": plan, "df": df, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    rendered = "\n".join(str(item.value) for item in app.get("markdown"))
    assert t(language, "summary_title") in rendered
    for key in ("summary_liquidity_label", "summary_margin_label",
                "summary_goal_label", "summary_purchasing_label"):
        assert t(language, key) in rendered
    assert t(language, "summary_goal_liquidity_warning") in rendered
    assert any(t(language, "summary_method_title") == item.label
               for item in app.get("expander"))
    assert app.session_state["plan"] == plan
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)



def test_zero_target_does_not_display_success_or_nominal_target_lines():
    plan = Plan(
        years=1, goal=0, initial_cash=3_000, monthly_income=1_600,
        monthly_expenses=1_400, monthly_investment=0)
    df = project(plan)
    wealth = wealth_figure(
        df, plan.goal, plan.start_year, plan.currency,
        WEALTH_SERIES, lambda k: t("en", k))
    assert len(wealth.data) == len(WEALTH_SERIES) - 2
    comparison = comparison_figure(
        build_comparisons(plan, 1, 3.0), plan.start_year, plan.currency,
        lambda k: t("en", k), plan.goal)
    assert not comparison.layout.shapes

    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = "en"
    app.session_state["plan"] = plan
    app.session_state["result"] = {
        "plan": plan, "df": df, "mc": None,
    }
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    goal_metric = next(
        metric for metric in app.get("metric")
        if metric.label == t("en", "goal_reached"))
    assert goal_metric.value == t("en", "not_applicable")
    rendered = "\n".join(str(item.value) for item in app.get("markdown"))
    assert t("en", "summary_goal_zero") in rendered
