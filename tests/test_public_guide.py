"""Keep the public guide informative without exposing internal implementation."""
from pathlib import Path
import re

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "Documentation" / "public"


@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_public_guide_has_twelve_sections_and_renderable_equations(language):
    source = (PUBLIC_DIR / f"guide_{language}.md").read_text(encoding="utf-8")
    headings = re.findall(r"(?m)^## (\d+)\. [^\n]+$", source)
    assert headings == [str(i) for i in range(1, 13)]
    assert sum(line.strip() == "$$" for line in source.splitlines()) == 8
    assert "N_m = C_m + A_m - D_m" in source
    assert r"\[" not in source and r"\]" not in source
    assert r"\(" not in source and r"\)" not in source
    for pattern in (r"\b[a-z_]+\.py\b", r"st\.[a-z_]+", r"Documentation/\d\d_",
                    r"schema_version", r"\.github/workflows", r"\btests/test_"):
        assert not re.search(pattern, source), (language, pattern)


@pytest.mark.parametrize("language", ["fr", "en", "vi"])
def test_streamlit_displays_curated_documentation_instead_of_raw_notes(language):
    app = AppTest.from_file(str(ROOT / "pages" / "guide.py"), default_timeout=20)
    app.session_state["language_choice"] = language
    app.run()
    assert not app.exception, app.exception
    assert len(app.get("expander")) == 12
    displayed = "\n".join(str(item.value) for item in app.get("markdown"))
    assert "N_m = C_m + A_m - D_m" in displayed
    assert "$$" in displayed
    assert "app.py" not in displayed
    assert "st.session_state" not in displayed
    assert "tests/test_" not in displayed


def test_app_guide_never_reads_original_technical_notes():
    source = (ROOT / "pages" / "guide.py").read_text(encoding="utf-8")
    assert '"Documentation" / "public"' in source
    assert "01_CAHIER_DES_CHARGES.md" not in source
    assert "02_MODELES_MATHEMATIQUES.md" not in source
    assert "Documentation/{filename}" not in source
