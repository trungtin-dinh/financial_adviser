"""Finite-difference sensitivity: numeric fidelity, semantics, and public UI."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import (
    SENSITIVITY_METRICS, assumption_sensitivity_figure,
)
from financial_adviser.engine import project
from financial_adviser.models import LifeEvent, Plan
from financial_adviser.sensitivity import (
    AMOUNT_FIELDS, RATE_FIELDS, analyze_assumptions,
)
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def test_every_impact_matches_independent_same_horizon_reprojection():
    plan = Plan(
        years=3, initial_cash=18_000, initial_investments=11_000,
        monthly_income=3_100, monthly_expenses=2_200,
        monthly_investment=500, investment_return_pct=5,
        cash_return_pct=1.4, inflation_pct=2.5,
        loan_balance=14_000, loan_apr_pct=3, loan_years=4,
        life_events=(
            LifeEvent("other", "Family support", 7, 4,
                      monthly_expense=300, upfront_cost=900),
        ),
    )
    original = project(plan)
    snapshot = original.copy(deep=True)
    report = analyze_assumptions(plan, 3)
    assert len(report.impacts) == 9
    assert report.years == plan.years
    assert report.baseline_final_nominal == pytest.approx(original.net_worth.iloc[-1])
    assert report.baseline_final_real == pytest.approx(original.net_worth_real.iloc[-1])
    assert report.baseline_minimum_cash == pytest.approx(original.cash.min())
    assert len({item.field for item in report.impacts}) == 9
    for item in report.impacts:
        tested = project(replace(plan, **{item.field: item.tested_value}))
        assert item.final_nominal_change == pytest.approx(
            float(tested.net_worth.iloc[-1] - original.net_worth.iloc[-1])
        )
        assert item.final_real_change == pytest.approx(
            float(tested.net_worth_real.iloc[-1] - original.net_worth_real.iloc[-1])
        )
        assert item.minimum_cash_change == pytest.approx(
            float(tested.cash.min() - original.cash.min())
        )
        if item.kind == "amount":
            assert item.field in AMOUNT_FIELDS
            assert item.change_size == pytest.approx(10.0)
            assert item.tested_value == pytest.approx(item.baseline_value * 1.10)
        else:
            assert item.field in RATE_FIELDS + ("loan_apr_pct",)
            assert item.change_size == pytest.approx(1.0)
            assert item.tested_value == pytest.approx(item.baseline_value + 1.0)
    assert plan.years == 3
    assert plan.loan_apr_pct == 3
    pd.testing.assert_frame_equal(project(plan), snapshot)


def test_inflation_changes_real_not_nominal_wealth_or_cash():
    plan = Plan(years=5, inflation_pct=2.0)
    report = analyze_assumptions(plan, 5)
    inflation = next(item for item in report.impacts
                     if item.field == "inflation_pct")
    assert inflation.final_nominal_change == pytest.approx(0.0, abs=1e-6)
    assert inflation.minimum_cash_change == pytest.approx(0.0, abs=1e-6)
    assert inflation.final_real_change < 0.0
    assert inflation.tested_value == pytest.approx(3.0)


def test_extra_investment_transfer_is_not_new_money():
    plan = Plan(
        years=3, initial_cash=20_000, monthly_income=2_000,
        monthly_expenses=1_200, monthly_investment=200,
        cash_return_pct=0.0, investment_return_pct=0.0,
    )
    impact = next(i for i in analyze_assumptions(plan, 3).impacts
                  if i.field == "monthly_investment")
    assert impact.final_nominal_change == pytest.approx(0.0, abs=1e-6)
    assert impact.minimum_cash_change < 0.0


def test_zero_amount_inputs_are_not_misleading_relative_sensitivity_cases():
    plan = Plan(
        years=1, initial_cash=0, monthly_income=0,
        monthly_expenses=0, monthly_investment=0, loan_balance=0,
    )
    report = analyze_assumptions(plan, 1)
    fields = [item.field for item in report.impacts]
    assert not set(fields).intersection(AMOUNT_FIELDS)
    assert "loan_apr_pct" not in fields
    assert fields == list(RATE_FIELDS)


def test_upper_rate_bound_uses_explicit_negative_one_point():
    plan = Plan(
        years=1, initial_cash=10_000, initial_investments=0,
        monthly_income=0, monthly_expenses=0, monthly_investment=0,
        investment_return_pct=200.0,
    )
    item = next(i for i in analyze_assumptions(plan, 1).impacts
                if i.field == "investment_return_pct")
    assert item.baseline_value == 200.0
    assert item.tested_value == 199.0
    assert item.change_size == -1.0


def test_aligned_horizon_and_schedule_constraints():
    plan = Plan(
        years=4, life_events=(LifeEvent(
            "relocation", "Move", 30, 2, monthly_expense=50),),
    )
    with pytest.raises(ValueError, match="horizon"):
        analyze_assumptions(plan, 2)
    report = analyze_assumptions(plan, 3)
    assert report.years == 3
    ref = project(replace(plan, years=3))
    assert report.baseline_final_nominal == pytest.approx(ref.net_worth.iloc[-1])
    assert plan.years == 4
    for invalid in (0, 61, 1.5, True):
        with pytest.raises(ValueError):
            analyze_assumptions(Plan(years=2), invalid)


@pytest.mark.parametrize("amount,rate", [
    (0, 1), (-1, 1), (101, 1),
    (10, 0), (10, -0.1), (10, 11),
    (float("nan"), 1), (10, float("inf")),
])
def test_invalid_perturbations_rejected(amount, rate):
    with pytest.raises(ValueError):
        analyze_assumptions(Plan(years=1), 1,
                            amount_change_pct=amount, rate_change_pp=rate)


@pytest.mark.parametrize("metric", SENSITIVITY_METRICS)
def test_bar_chart_values_are_signed_and_have_valid_currency(metric):
    report = analyze_assumptions(Plan(years=2), 2)
    fig = assumption_sensitivity_figure(
        report, metric, "EUR", lambda key: t("fr", key))
    assert len(fig.data) == 1
    values = [getattr(row, metric) for row in report.impacts]
    np.testing.assert_allclose(fig.data[0].x, values)
    assert len(fig.data[0].y) == len(values)
    assert fig.data[0].orientation == "h"
    assert "EUR" in fig.layout.xaxis.title.text
    assert fig.layout.yaxis.autorange == "reversed"
    with pytest.raises(ValueError):
        assumption_sensitivity_figure(
            report, "unknown_measure", "EUR", lambda key: key)


@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_user_can_calculate_and_change_output_without_editing_saved_plan(language):
    plan = Plan(years=2, initial_cash=1200, monthly_income=2200,
                monthly_expenses=1700, monthly_investment=100)
    df = project(plan)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=40)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = plan
    app.session_state["result"] = {"plan": plan, "df": df, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert any(ex.label == t(language, "sens_title")
               for ex in app.get("expander"))
    assert app.session_state.get("_sensitivity_cache") is None
    app.button(key="sensitivity_run").click().run()
    assert not app.exception, app.exception
    cache = app.session_state["_sensitivity_cache"]
    assert cache["plan"] == plan
    assert cache["report"].years == 2
    assert len(cache["report"].impacts) >= 5
    selector = app.segmented_control(key="sensitivity_metric")
    assert selector.value == "final_real_change"
    app.segmented_control(key="sensitivity_metric").set_value(
        "minimum_cash_change").run()
    assert not app.exception, app.exception
    assert app.session_state["_sensitivity_cache"]["report"] == cache["report"]
    app.checkbox(key="sensitivity_show_table").set_value(True).run()
    assert not app.exception, app.exception
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
    assert app.session_state["plan"] == plan
    app.number_input(key="comparison_horizon").set_value(3).run()
    assert not app.exception, app.exception
    assert app.session_state.get("_sensitivity_cache") is None
