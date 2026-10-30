"""Regression checks for aligned comparisons and optional event markers."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import (
    MAX_EVENT_LINES, comparison_figure, event_markers,
    overlay_event_markers, wealth_figure,
)
from financial_adviser.comparisons import (
    build_comparisons, minimum_comparison_years,
)
from financial_adviser.engine import project
from financial_adviser.households import AdultBudget, ChildBudget, DependentBudget
from financial_adviser.models import LifeEvent, OneOff, Plan
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def plan_with_obligations() -> Plan:
    return Plan(
        years=6, one_offs=(OneOff(month=23, amount=-150, description="Fees"),),
        life_events=(
            LifeEvent("relocation", "Move", first_month=32,
                      duration_months=8, monthly_expense=75),
        ),
        children=(ChildBudget(label="Child", age_years=0,
                              arrival_month=49, support_until_age=2),),
        dependents=(DependentBudget(label="Parent", first_month=49,
                                    duration_months=12, monthly_support=35),),
    )


def test_comparison_minimum_horizon_retains_dated_obligations():
    p = plan_with_obligations()
    assert minimum_comparison_years(p) == 5
    with pytest.raises(ValueError, match="excludes a dated obligation"):
        build_comparisons(p, years=4, return_shock_pct=3.0)
    assert len(build_comparisons(p, years=5, return_shock_pct=3.0)) == 5
    assert p.years == 6


@pytest.mark.parametrize("years", [5, 6, 9])
def test_comparison_differences_use_same_horizon_reference(years):
    p = plan_with_obligations()
    reference = replace(p, years=years)
    expected = project(reference)
    cases = build_comparisons(p, years=years, return_shock_pct=2.5)
    assert [case.key for case in cases] == [
        "scenario_lower", "scenario_base", "scenario_higher",
        "scenario_no_events", "scenario_events_more",
    ]
    baseline = next(c for c in cases if c.key == "scenario_base")
    pd.testing.assert_frame_equal(baseline.projection, expected)
    assert baseline.terminal_delta == pytest.approx(0)
    assert baseline.terminal_real == pytest.approx(
        float(expected.net_worth_real.iloc[-1])
    )
    for case in cases:
        assert len(case.projection) == years * 12 + 1
        assert case.terminal_delta == pytest.approx(
            case.terminal_nominal - baseline.terminal_nominal)
        assert case.minimum_cash == pytest.approx(case.projection.cash.min())
        assert case.goal_reached == (case.terminal_nominal >= p.goal)
    assert p.years == 6
    assert p.life_events[0].monthly_expense == 75


def test_comparison_figure_has_aligned_dates_and_nominal_values():
    p = plan_with_obligations()
    cases = build_comparisons(p, 5, 3.0)
    fig = comparison_figure(cases, p.start_year, p.currency,
                            lambda k: t("fr", k), p.goal)
    assert len(fig.data) == len(cases)
    assert len(fig.layout.shapes) == 1  # nominal goal is valid on this axis
    for trace, case in zip(fig.data, cases):
        np.testing.assert_allclose(trace.y, case.projection.net_worth)
        np.testing.assert_array_equal(trace.x, case.projection.month)
    assert next(c for c in fig.data if c.name == t("fr", "scenario_base")).line.width > 3


def test_comparison_validation_rejects_bad_horizons_and_shocks():
    plan = Plan(years=2)
    for years, shock in [(0, 3.0), (61, 3.0), (2.3, 3.0),
                         (2, float("nan")), (2, 0.2), (2, 11.0)]:
        with pytest.raises(ValueError):
            build_comparisons(plan, years, shock)


def test_event_markers_show_dates_without_changing_wealth():
    p = Plan(
        years=5, one_offs=(OneOff(month=3, amount=-1200,
                                  description="Deposit"),),
        life_events=(LifeEvent("relocation", "Move", 3, 4,
                               monthly_expense=40),),
        children=(ChildBudget("New child", age_years=0, arrival_month=1,
                              support_until_age=2),),
        adults=(AdultBudget("Adult", age_years=62, retirement_age=65),),
        dependents=(DependentBudget("Relative", first_month=5,
                                    duration_months=2),),
    )
    markers = event_markers(p)
    positions = [(m.kind, m.month) for m in markers]
    assert ("event_start", 3) in positions
    assert ("event_end", 7) in positions
    assert ("oneoff", 3) in positions
    assert ("child_arrival", 1) in positions
    assert ("child_support_end", 25) in positions
    assert ("dependent_start", 5) in positions
    assert ("dependent_end", 7) in positions
    assert ("retirement", 37) in positions

    df = project(p)
    fig = wealth_figure(df, p.goal, p.start_year, p.currency,
                        ("net_worth",), lambda k: t("en", k))
    original = np.asarray(fig.data[0].y).copy()
    drawn, unique = overlay_event_markers(fig, markers)
    assert drawn == unique == len({m.month for m in markers})
    assert len(fig.layout.shapes) == unique
    np.testing.assert_array_equal(fig.data[0].y, original)
    assert p.years == 5


def test_too_many_event_dates_are_listed_but_not_all_drawn():
    plan = Plan(years=3, one_offs=tuple(
        OneOff(month=m, amount=-10, description=f"Item {m}")
        for m in range(1, 21)
    ))
    events = event_markers(plan)
    chart = wealth_figure(project(plan), plan.goal, plan.start_year,
                          plan.currency, ("cash",), lambda key: t("fr", key))
    drawn, total = overlay_event_markers(chart, events)
    assert drawn == MAX_EVENT_LINES
    assert total == 20
    assert len(events) == 20
    assert len(chart.layout.shapes) == MAX_EVENT_LINES


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_event_marker_and_horizon_controls_preserve_calculated_plan(lang):
    plan = plan_with_obligations()
    result = project(plan)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = lang
    app.session_state["plan"] = plan
    app.session_state["result"] = {"plan": plan, "df": result, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert app.checkbox(key="chart_show_events").value is False
    # The default Results view does not render unrelated comparison controls.
    assert not any(x.key == "comparison_horizon" for x in app.get("number_input"))
    app.checkbox(key="chart_show_events").set_value(True).run()
    assert not app.exception, app.exception
    assert any(t(lang, "chart_event_list") in x.label
               for x in app.get("expander"))
    app.session_state["main_results_navigation"] = t(lang, "tab_compare")
    app.run()
    assert not app.exception, app.exception
    assert app.number_input(key="comparison_horizon").value == plan.years
    app.number_input(key="comparison_horizon").set_value(5).run()
    assert not app.exception, app.exception
    assert app.number_input(key="comparison_horizon").value == 5
    assert app.session_state["plan"] == plan
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], result)
    assert app.session_state["result"]["plan"].years == plan.years
