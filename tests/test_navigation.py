"""Lazy navigation: only the selected analysis is evaluated and rendered."""
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.engine import project
from financial_adviser.models import Plan
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


def fixture_app(language: str, *, main: str = "tab_results",
                sub: str = "analysis_variants") -> tuple[AppTest, Plan, pd.DataFrame]:
    plan = Plan(years=3)
    result = project(plan)
    app = AppTest.from_file(
        str(ROOT / "pages" / "planning.py"), default_timeout=40)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = plan
    app.session_state["result"] = {"plan": plan, "df": result, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.session_state["main_results_navigation"] = t(language, main)
    app.session_state["comparison_analysis_navigation"] = t(language, sub)
    app.run()
    assert not app.exception, app.exception
    return app, plan, result


@pytest.mark.parametrize("language", ("fr", "en", "vi"))
def test_default_results_render_without_hidden_comparison_controls(language):
    app, plan, df = fixture_app(language)
    assert [tab.label for tab in app.tabs] == [
        t(language, key)
        for key in ("tab_results", "tab_goal", "tab_compare")
    ]
    assert any(str(x.value) == t(language, "tab_results")
               for x in app.get("subheader"))
    assert app.segmented_control(key="result_chart_view") is not None
    assert not any(item.key == "comparison_horizon"
                   for item in app.get("number_input"))
    assert not any(item.key == "stress_start_month"
                   for item in app.get("number_input"))
    assert not any(item.key == "sensitivity_run"
                   for item in app.get("button"))
    assert not any(item.key == "custom_compare_submit"
                   for item in app.get("button"))
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
    assert app.session_state["plan"] == plan


@pytest.mark.parametrize("language", ("fr", "en", "vi"))
@pytest.mark.parametrize("analysis,expected_key", (
    ("analysis_variants", "compare_return_shock"),
    ("analysis_custom", "custom_compare_submit"),
    ("analysis_sensitivity", "sensitivity_run"),
    ("analysis_stress", "stress_start_month"),
))
def test_only_selected_comparison_view_instantiates_its_controls(language, analysis, expected_key):
    app, plan, df = fixture_app(language, main="tab_compare", sub=analysis)
    assert [tab.label for tab in app.tabs] == [
        t(language, key) for key in (
            "tab_results", "tab_goal", "tab_compare",
            "analysis_variants", "analysis_custom",
            "analysis_sensitivity", "analysis_stress"
        )
    ]
    assert app.number_input(key="comparison_horizon").value == plan.years
    all_control_keys = {
        x.key for collection in ("number_input", "button", "multiselect")
        for x in app.get(collection) if x.key is not None
    }
    for other in ("compare_return_shock", "custom_compare_submit",
                  "sensitivity_run", "stress_start_month"):
        assert (other in all_control_keys) == (other == expected_key)
    assert not any(str(x.value) == t(language, "summary_title")
                   for x in app.get("markdown"))
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)


def test_navigation_without_any_calculated_result_remains_simple():
    app = AppTest.from_file(
        str(ROOT / "pages" / "planning.py"), default_timeout=25)
    app.session_state["language_choice"] = "fr"
    app.run()
    assert not app.exception, app.exception
    assert len(app.tabs) == 0
    assert app.number_input(key="field_income") is not None
    assert app.number_input(key="field_expenses") is not None
    assert app.button(key="run_projection") is not None


@pytest.mark.parametrize("language", ("fr", "en", "vi"))
def test_changing_comparison_controls_does_not_mutate_saved_projection(language):
    app, plan, df = fixture_app(language, main="tab_compare", sub="analysis_stress")
    app.number_input(key="stress_start_month").set_value(4).run()
    assert not app.exception, app.exception
    assert app.number_input(key="stress_start_month").value == 4
    assert app.session_state["plan"] == plan
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)


def test_hidden_tabs_skip_heavy_scenario_work(monkeypatch):
    """The important optimization is skipping whole analyses, not only plots."""
    import financial_adviser.planning_analysis_ui as analysis_ui

    counts = {"preset": 0, "stress": 0}
    original_presets = analysis_ui.build_comparisons
    original_stresses = analysis_ui.evaluate_stresses

    def counted_presets(*args, **kwargs):
        counts["preset"] += 1
        return original_presets(*args, **kwargs)

    def counted_stresses(*args, **kwargs):
        counts["stress"] += 1
        return original_stresses(*args, **kwargs)

    monkeypatch.setattr(analysis_ui, "build_comparisons", counted_presets)
    monkeypatch.setattr(analysis_ui, "evaluate_stresses", counted_stresses)

    app, _, _ = fixture_app("en")
    assert counts == {"preset": 0, "stress": 0}

    app.session_state["main_results_navigation"] = t("en", "tab_compare")
    app.run()
    assert not app.exception, app.exception
    assert counts["preset"] >= 1
    assert counts["stress"] == 0
