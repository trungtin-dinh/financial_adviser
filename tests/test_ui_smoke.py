"""Streamlit AppTest smoke check: the local app page loads in each language."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_planner_renders_with_required_inputs_and_event_controls(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=20)
    app.session_state["language_choice"] = lang
    app.run()
    assert not app.exception, app.exception
    # Every primary form must be accessible without loading a sample.
    assert app.number_input(key="field_income") is not None
    assert app.number_input(key="field_expenses") is not None
    assert app.number_input(key="field_goal") is not None
    assert any(t(lang, "life_title") in str(item.value) for item in app.get("subheader"))
    assert any(t(lang, "advanced") in str(item.value) for item in app.get("subheader"))
    assert any(t(lang, "tab_results") in str(item.value) for item in app.get("subheader"))
    assert app.number_input(key="field_years") is not None
    assert app.selectbox(key="preset_selected") is not None
    assert any("Household" in str(x.value) or "foyer" in str(x.value).lower() or "gia đình" in str(x.value).lower() for x in app.get("subheader"))

@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_documentation_and_sources_load(lang):
    for path in ("guide.py", "sources.py"):
        app = AppTest.from_file(str(ROOT / "pages" / path), default_timeout=20)
        app.session_state["language_choice"] = lang
        app.run()
        assert not app.exception, (lang, path, app.exception)

def test_example_confirmation_restores_required_inputs_and_calculates():
    """Regression for hosted-app failure: demo then Run must never say fields are missing."""
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = "fr"
    app.run()
    assert not app.exception, app.exception
    app.button(key="load_demo").click().run()
    assert not app.exception, app.exception
    app.button(key="confirm_example").click().run()
    assert not app.exception, app.exception
    assert app.number_input(key="field_income").value == pytest.approx(3000.0)
    assert app.number_input(key="field_expenses").value == pytest.approx(2000.0)
    assert app.number_input(key="field_goal").value == pytest.approx(100000.0)
    app.button(key="run_projection").click().run()
    assert not app.exception, app.exception
    assert app.session_state["result"] is not None
