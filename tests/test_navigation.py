"""Navigation regression: results, goals and four self-contained analyses."""
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.engine import project
from financial_adviser.models import Plan
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("language", ("fr", "en", "vi"))
def test_analysis_is_organized_into_seven_translated_tabs(language):
    p = Plan(years=2)
    df = project(p)
    app = AppTest.from_file(
        str(ROOT / "pages" / "planning.py"), default_timeout=40)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = p
    app.session_state["result"] = {"plan": p, "df": df, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()

    assert not app.exception, app.exception
    expected = (
        "tab_results", "tab_goal", "tab_compare",
        "analysis_variants", "analysis_custom",
        "analysis_sensitivity", "analysis_stress",
    )
    assert [tab.label for tab in app.tabs] == [
        t(language, label) for label in expected
    ]
    # Eager tabs retain the original controls and don't need an extra
    # calculation to restore a previously analyzed scenario.
    assert app.number_input(key="comparison_horizon").value == p.years
    assert app.number_input(key="compare_return_shock").value == 3.0
    assert app.button(key="custom_compare_submit") is not None
    assert app.button(key="sensitivity_run") is not None
    assert app.number_input(key="stress_start_month") is not None
    assert any(str(header.value) == t(language, "tab_results")
               for header in app.tabs[0].get("subheader"))
    assert any(str(header.value) == t(language, "tab_goal")
               for header in app.tabs[1].get("subheader"))
    assert any(str(header.value) == t(language, "sens_title")
               for header in app.tabs[5].get("subheader"))

    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
    assert app.session_state["plan"] == p


def test_uncomputed_inputs_are_not_obscured_by_results_navigation():
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
def test_switching_comparison_view_does_not_modify_saved_projection(language):
    """UI tab organization is presentation only; calculations must persist."""
    p = Plan(years=3)
    df = project(p)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=40)
    app.session_state["language_choice"] = language
    app.session_state["plan"] = p
    app.session_state["result"] = {"plan": p, "df": df, "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception

    # Change a what-if input in another tab. The reference remains intact.
    app.number_input(key="stress_start_month").set_value(4).run()
    assert not app.exception, app.exception
    app.number_input(key="compare_return_shock").set_value(4.0).run()
    assert not app.exception, app.exception
    assert [tab.label for tab in app.tabs][:3] == [
        t(language, k) for k in ("tab_results", "tab_goal", "tab_compare")
    ]
    assert app.number_input(key="stress_start_month").value == 4
    assert app.number_input(key="compare_return_shock").value == 4.0
    assert app.session_state["plan"] == p
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
