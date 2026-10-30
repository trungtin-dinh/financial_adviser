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
    assert any(t(lang, "advanced") in item.label for item in app.get("expander"))
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
def test_new_cards_are_collapsed_and_deletable_without_opening(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = lang
    app.run()
    for add, toggle, remove in (
        ("household_add_child", "child_1_toggle", "child_1_remove"),
        ("household_add_dependent", "dependent_1_toggle", "dependent_1_remove"),
        ("household_add_adult", "adult_1_toggle", "adult_1_remove"),
        ("add_life_event", "evt_1_toggle", "evt_1_remove"),
    ):
        app.button(key=add).click().run()
        assert not app.exception, app.exception
        assert app.button(key=toggle) is not None
        assert app.button(key=remove) is not None
    assert not app.session_state.get("child_1_open", False)
    assert not app.session_state.get("dependent_1_open", False)
    assert not app.session_state.get("adult_1_open", False)
    assert not app.session_state.get("evt_1_open", False)
    assert not any("Modifier / réduire" in str(b.label) for b in app.get("button"))

    # Expand and collapse without deleting draft data, then remove while closed.
    app.button(key="child_1_toggle").click().run()
    assert app.number_input(key="child_1_age") is not None
    app.button(key="child_1_toggle").click().run()
    assert not app.session_state.get("child_1_open")
    app.button(key="child_1_remove").click().run()
    assert not app.session_state["household_children"]


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_other_dependent_can_be_configured_and_used(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"), default_timeout=30)
    app.session_state["language_choice"] = lang
    app.run()
    app.button(key="household_add_dependent").click().run()
    app.button(key="dependent_1_toggle").click().run()
    assert app.number_input(key="dependent_1_support") is not None
    assert app.number_input(key="dependent_1_care") is not None
    assert not app.exception, app.exception


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
