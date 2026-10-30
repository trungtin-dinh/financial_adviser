"""Risk dashboard: deterministic liquidity, no implied event probabilities."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import stress_liquidity_figure
from financial_adviser.engine import project
from financial_adviser.models import LifeEvent, Plan
from financial_adviser.scenarios import (
    PRESET_IDS, evaluate_stresses, proposed_event, stress_impact,
)
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def low_buffer_plan() -> Plan:
    return Plan(
        years=2, initial_cash=100, initial_investments=0,
        monthly_income=1000, monthly_expenses=950,
        monthly_investment=0, cash_return_pct=0,
        investment_return_pct=0, income_growth_pct=0,
        expense_growth_pct=0, inflation_pct=0,
    )


def test_stress_deficit_metrics_are_mathematically_consistent():
    base = low_buffer_plan()
    outcomes = evaluate_stresses(base, ("job_gap",), first_month=4)
    assert len(outcomes) == 1
    result = outcomes[0]
    assert result.impact.key == "job_gap"
    assert result.impact.event.first_month == 4
    assert result.impact.event.duration_months == 3
    assert result.first_deficit_month == 4
    assert result.deficit_months > 0
    assert result.newly_negative_months == result.deficit_months
    assert result.baseline_funding_need == 0
    assert result.peak_funding_need == pytest.approx(
        max(0, -float(result.stressed.cash.min())))
    assert result.impact.liquidity_breach
    assert result.impact.terminal_delta == pytest.approx(
        float(result.stressed.net_worth.iloc[-1] -
              result.baseline.net_worth.iloc[-1]))
    pd.testing.assert_frame_equal(result.baseline, project(base))
    assert stress_impact(base, "job_gap", 4) == result.impact
    assert base.life_events == ()


def test_existing_baseline_deficit_is_not_attributed_to_stress():
    base = replace(low_buffer_plan(),
                   monthly_income=0, monthly_expenses=150,
                   initial_cash=0, years=1)
    evaluation = evaluate_stresses(base, ("unexpected_purchase",), 1)[0]
    assert evaluation.baseline_funding_need > 0
    assert evaluation.peak_funding_need >= evaluation.baseline_funding_need
    assert evaluation.first_deficit_month == 1
    assert evaluation.deficit_months == 12
    assert evaluation.newly_negative_months == 0


def test_stress_start_and_end_of_horizon_are_explicit():
    p = low_buffer_plan()
    early = evaluate_stresses(p, ("unexpected_purchase",), first_month=2)[0]
    late = evaluate_stresses(p, ("unexpected_purchase",), first_month=24)[0]
    assert early.impact.event.first_month == 2
    assert late.impact.event.first_month == 24
    assert len(late.stressed) == len(early.stressed) == 25
    assert early.impact.terminal_delta != late.impact.terminal_delta or early.first_deficit_month != late.first_deficit_month
    clipped = evaluate_stresses(p, ("child_care",), 24)[0]
    assert clipped.impact.event.duration_months == 1
    with pytest.raises(ValueError):
        evaluate_stresses(p, ("job_gap",), 25)


def test_independent_shocks_do_not_mutate_reference_plan_or_accumulate():
    plan = replace(low_buffer_plan(), life_events=(
        LifeEvent("relocation", "Existing cost", 7, 2, monthly_expense=10),))
    outcomes = evaluate_stresses(plan, ("job_gap", "health_costs", "relocation"), 5)
    assert len(outcomes) == 3
    assert len({id(e.baseline) for e in outcomes}) == 1
    for outcome in outcomes:
        assert len(outcome.stressed) == len(outcome.baseline)
        pd.testing.assert_frame_equal(outcome.baseline, project(plan))
    assert len(plan.life_events) == 1
    assert len(evaluate_stresses(plan, (), 5)) == 0


@pytest.mark.parametrize("keys,start", [
    (("job_gap", "job_gap"), 1),
    (("invalid",), 1),
    (("job_gap",), 0),
    (("job_gap",), 25),
    (("job_gap",), True),
])
def test_stress_validation_rejects_invalid_requests(keys, start):
    with pytest.raises(ValueError):
        evaluate_stresses(low_buffer_plan(), keys, start)


def test_stress_chart_matches_cash_trajectories_and_shows_unfunded_zone():
    case = evaluate_stresses(low_buffer_plan(), ("job_gap",), 4)[0]
    fig = stress_liquidity_figure(
        case, 2026, "EUR", lambda key: t("en", key))
    assert len(fig.data) == 2
    np.testing.assert_allclose(fig.data[0].y, case.baseline.cash)
    np.testing.assert_allclose(fig.data[1].y, case.stressed.cash)
    assert fig.data[0].name == t("en", "scenario_base")
    assert fig.data[1].name == t("en", "preset_job_gap")
    assert fig.data[0].line.dash == "solid"
    assert fig.data[1].line.dash == "dash"
    assert fig.layout.yaxis.title.text == "EUR"
    # Zero threshold, unfunded zone and stress duration.
    assert len(fig.layout.shapes) == 3
    assert "Probability" not in str(fig.layout)


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_risk_controls_work_without_editing_reference(lang):
    plan = low_buffer_plan()
    reference = project(plan)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = lang
    app.session_state["plan"] = plan
    app.session_state["result"] = {
        "plan": plan, "df": reference, "mc": None,
    }
    app.session_state["confirmed_inputs"] = True
    app.session_state["main_results_navigation"] = t(lang, "tab_compare")
    app.session_state["comparison_analysis_navigation"] = t(lang, "analysis_stress")
    app.run()
    assert not app.exception, app.exception
    assert app.number_input(key="stress_start_month").value == 1
    assert app.selectbox(key="stress_focus_selected").value == "job_gap"
    assert any(t(lang, "stress_peak_need") in item.label
               for item in app.get("metric"))
    app.number_input(key="stress_start_month").set_value(4).run()
    assert not app.exception, app.exception
    app.selectbox(key="stress_focus_selected").set_value("unexpected_purchase").run()
    assert not app.exception, app.exception
    assert app.session_state["plan"] == plan
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], reference)
    app.multiselect(key="stress_selection").set_value([]).run()
    assert not app.exception, app.exception
    assert any(t(lang, "stress_select_one") in str(item.value)
               for item in app.get("info"))


def test_well_funded_scenario_reports_no_simulated_cash_deficit():
    base = replace(low_buffer_plan(), initial_cash=200_000)
    evaluation = evaluate_stresses(base, ("unexpected_purchase",), 2)[0]
    assert evaluation.first_deficit_month is None
    assert evaluation.deficit_months == 0
    assert evaluation.newly_negative_months == 0
    assert evaluation.peak_funding_need == 0.0
    assert evaluation.baseline_funding_need == 0.0


def test_multiple_shocks_reuse_a_single_baseline_projection(monkeypatch):
    import financial_adviser.engine as engine

    original_project = engine.project
    count = 0

    def counted(plan):
        nonlocal count
        count += 1
        return original_project(plan)

    monkeypatch.setattr(engine, "project", counted)
    evaluations = evaluate_stresses(
        low_buffer_plan(), ("job_gap", "health_costs", "relocation"), 3)
    assert len(evaluations) == 3
    assert count == 4  # One reference + one projection per independent shock.
