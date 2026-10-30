"""Two fully personalized scenarios: aligned math, boundaries, and Streamlit UI."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import custom_comparison_figure
from financial_adviser.custom_comparison import (
    CUSTOM_FIELDS, compare_custom_scenarios, make_custom_variant,
)
from financial_adviser.engine import project
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import LifeEvent, OneOff, Plan
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def baseline() -> Plan:
    return Plan(
        years=6, initial_cash=12_000, initial_investments=9_000,
        monthly_income=3_000, monthly_expenses=2_000,
        monthly_investment=300, investment_return_pct=4.0,
        cash_return_pct=1.0, inflation_pct=2.0,
        goal=100_000,
        loan_balance=15_000, loan_apr_pct=3.5, loan_years=7,
        life_events=(LifeEvent("relocation", "Move", 14, 3,
                               monthly_expense=170, upfront_cost=600),),
    )


def test_several_independent_assumption_changes_are_reprojected_together():
    base = baseline()
    adjustments = {
        "monthly_income": 3500, "monthly_expenses": 1900,
        "monthly_investment": 450, "investment_return_pct": 5.5,
        "loan_years": 5,
    }
    variant = make_custom_variant(base, adjustments)
    assert variant != base
    assert base.monthly_income == 3000
    assert variant.monthly_income == 3500
    assert variant.monthly_expenses == 1900
    assert variant.loan_years == 5
    assert variant.life_events == base.life_events

    result = compare_custom_scenarios(base, variant, 6)
    original = project(base)
    changed = project(variant)
    pd.testing.assert_frame_equal(result.reference, original)
    pd.testing.assert_frame_equal(result.alternative, changed)
    assert result.years == 6
    assert result.nominal_difference == pytest.approx(
        changed.net_worth.iloc[-1] - original.net_worth.iloc[-1])
    assert result.real_difference == pytest.approx(
        changed.net_worth_real.iloc[-1] - original.net_worth_real.iloc[-1])
    assert result.minimum_cash_difference == pytest.approx(
        changed.cash.min() - original.cash.min())
    assert result.reference_funding_gap == pytest.approx(
        max(0.0, -original.cash.min()))
    assert result.alternative_funding_gap == pytest.approx(
        max(0.0, -changed.cash.min()))
    assert base.years == 6


def test_complete_imported_plan_supports_different_life_events():
    base = baseline()
    other = replace(
        base, years=7, monthly_income=4200,
        life_events=(
            LifeEvent("education", "Training", 27, 8,
                      monthly_expense=340, upfront_cost=1000),
        ),
        one_offs=(OneOff(55, -1600, "Equipment"),),
    )
    imported = load_plan(dump_plan(other))
    comparison = compare_custom_scenarios(base, imported, 6)
    assert comparison.alternative_plan.years == 6
    assert comparison.alternative_plan.life_events == imported.life_events
    assert comparison.reference_plan.life_events == base.life_events
    assert len(comparison.reference) == len(comparison.alternative) == 73
    pd.testing.assert_frame_equal(
        comparison.alternative, project(replace(other, years=6)))
    assert imported.years == 7
    assert comparison.reference_goal_reached in (True, False)
    assert comparison.alternative_goal_reached in (True, False)


@pytest.mark.parametrize("field,value", [
    ("currency", "VND"), ("country", "VN"),
    ("start_year", 2027), ("goal", 150_000),
])
def test_mismatched_comparison_context_is_rejected(field, value):
    base = baseline()
    with pytest.raises(ValueError, match="Different"):
        compare_custom_scenarios(base, replace(base, **{field: value}), 6)


def test_horizon_cannot_drop_variant_events_or_reference_obligations():
    base = baseline()
    other = replace(
        base, years=8,
        life_events=(LifeEvent("other", "Later event", 76, 3,
                               monthly_expense=100),),
    )
    with pytest.raises(ValueError, match="dated obligations"):
        compare_custom_scenarios(base, other, 6)
    comparison = compare_custom_scenarios(base, other, 7)
    assert comparison.years == 7
    assert comparison.alternative_plan.life_events[0].first_month == 76
    for years in (0, 61, True, 2.5):
        with pytest.raises(ValueError):
            compare_custom_scenarios(base, base, years)


@pytest.mark.parametrize("changes", [
    {"goal": 10}, {"country": "VN"}, {"unknown": 3},
    {"monthly_income": -1}, {"cash_return_pct": -99},
    {"loan_years": 0}, {"loan_years": 3.5},
    {"loan_years": True}, {"investment_return_pct": float("nan")},
    {"initial_cash": float("inf")},
])
def test_custom_changes_validated_and_allowlisted(changes):
    with pytest.raises(ValueError):
        make_custom_variant(baseline(), changes)
    assert "goal" not in CUSTOM_FIELDS


def test_same_plan_gives_zero_differences_but_cash_issues_remain_visible():
    base = Plan(
        years=2, monthly_income=0, monthly_expenses=2500,
        initial_cash=0, initial_investments=200_000,
        monthly_investment=0, goal=100_000,
    )
    comparison = compare_custom_scenarios(base, base, 2)
    assert comparison.nominal_difference == pytest.approx(0)
    assert comparison.real_difference == pytest.approx(0)
    assert comparison.minimum_cash_difference == pytest.approx(0)
    assert comparison.reference_deficit_months == 24
    assert comparison.alternative_deficit_months == 24
    assert comparison.reference_funding_gap > 0
    assert comparison.reference_goal_reached


def test_no_target_means_no_false_goal_success():
    base = replace(baseline(), goal=0)
    comparison = compare_custom_scenarios(base, base, 6)
    assert comparison.reference_goal_reached is None
    assert comparison.alternative_goal_reached is None
    chart = custom_comparison_figure(
        comparison, "net_worth", "EUR",
        lambda key: t("fr", key))
    assert len(chart.data) == 2
    assert not chart.layout.shapes


@pytest.mark.parametrize("field", ["net_worth", "net_worth_real", "cash"])
@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_two_curve_visualization_is_aligned_and_metric_consistent(field, language):
    base = baseline()
    variant = make_custom_variant(base, {
        "monthly_income": 3200, "inflation_pct": 3.0,
    })
    result = compare_custom_scenarios(base, variant, 6)
    fig = custom_comparison_figure(
        result, field, base.currency,
        lambda key: t(language, key))
    assert len(fig.data) == 2
    np.testing.assert_allclose(fig.data[0].y, result.reference[field])
    np.testing.assert_allclose(fig.data[1].y, result.alternative[field])
    np.testing.assert_array_equal(fig.data[0].x, fig.data[1].x)
    assert fig.data[0].name == t(language, "custom_reference")
    assert fig.data[1].name == t(language, "custom_variant")
    assert fig.layout.yaxis.title.text == base.currency
    assert len(fig.layout.shapes) == (1 if field in ("cash", "net_worth") else 0)
    with pytest.raises(ValueError):
        custom_comparison_figure(result, "unknown", "EUR", lambda key: key)


@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_custom_form_and_result_selectors_keep_reference_unchanged(language):
    base = baseline()
    saved_df = project(base)
    app = AppTest.from_file(
        str(ROOT / "pages" / "planning.py"), default_timeout=40)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = base
    app.session_state["result"] = {
        "plan": base, "df": saved_df, "mc": None,
    }
    app.session_state["confirmed_inputs"] = True
    app.session_state["main_results_navigation"] = t(language, "tab_compare")
    app.session_state["comparison_analysis_navigation"] = t(language, "analysis_custom")
    app.run()
    assert not app.exception, app.exception
    assert any(str(x.value) == t(language, "custom_title")
               for x in app.get("subheader"))
    assert app.session_state.get("_custom_comparison") is None
    assert app.radio(key="custom_input_mode").value == "edit"
    app.number_input(key="custom_field_monthly_income").set_value(3500.0)
    app.number_input(key="custom_field_monthly_expenses").set_value(1800.0)
    app.button(key="custom_compare_submit").click().run()
    assert not app.exception, app.exception
    result = app.session_state["_custom_comparison"]
    assert result["result"].alternative_plan.monthly_income == pytest.approx(3500)
    assert result["result"].alternative_plan.monthly_expenses == pytest.approx(1800)
    assert result["result"].nominal_difference > 0
    assert app.segmented_control(key="custom_metric").value == "net_worth_real"
    app.segmented_control(key="custom_metric").set_value("cash").run()
    assert not app.exception, app.exception
    assert app.session_state["plan"] == base
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], saved_df)
    # Changing the common horizon invalidates old comparison results.
    app.number_input(key="comparison_horizon").set_value(7).run()
    assert not app.exception, app.exception
    assert app.session_state.get("_custom_comparison") is None
