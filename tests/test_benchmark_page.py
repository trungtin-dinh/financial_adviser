"""Streamlit checks: reference page renders in every language without network access."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from financial_adviser.benchmark_i18n import b

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_reference_page_renders_with_official_observations(lang):
    app = AppTest.from_file(str(ROOT / "pages" / "benchmarks.py"), default_timeout=25)
    app.session_state["language_choice"] = lang
    app.run()
    assert not app.exception, (lang, app.exception)
    assert any(b(lang, "title") in str(item.value) for item in app.title)
    assert len(app.metric) >= 2
    assert all("EUR" in str(m.value) for m in app.metric if lang and app.session_state.plan.country == "FR")
