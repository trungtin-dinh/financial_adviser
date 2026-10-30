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
    # No results placeholder before the user explicitly runs a projection.
    assert not any(t(lang, "tab_results") == str(item.value) for item in app.get("subheader"))
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

@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_child_and_adult_cards_are_collapsible(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = lang
    app.run()
    app.button(key="household_add_child").click().run()
    assert not app.exception, app.exception
    child_expanders = [e for e in app.get("expander") if "👶" in str(e.label)]
    assert len(child_expanders) == 1
    # The date is shown in the separate compact summary, not in the stable toggle label.
    app.button(key="household_add_adult").click().run()
    assert not app.exception, app.exception
    adult_expanders = [e for e in app.get("expander") if "🧑" in str(e.label)]
    assert len(adult_expanders) == 1
    assert app.number_input(key="child_1_age").value == 0
    assert app.number_input(key="child_1_support").value == 25

@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_event_card_has_compact_summary(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = lang
    app.run()
    app.button(key="add_life_event").click().run()
    assert not app.exception, app.exception
    events = [e for e in app.get("expander") if "📅" in str(e.label)]
    assert len(events) == 1
    # The date is shown in the separate compact summary, not in the stable toggle label.
    assert app.text_input(key="evt_1_label") is not None

def test_results_only_after_explicit_run():
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = "fr"
    app.run()
    assert not any(str(x.value) == t("fr", "tab_results") for x in app.get("subheader"))
    app.button(key="load_demo").click().run()
    app.button(key="confirm_example").click().run()
    # Loading demo alone must not reveal a previously computed result.
    assert not any(str(x.value) == t("fr", "tab_results") for x in app.get("subheader"))
    app.button(key="run_projection").click().run()
    assert not app.exception, app.exception
    assert any(str(x.value) == t("fr", "tab_results") for x in app.get("subheader"))
