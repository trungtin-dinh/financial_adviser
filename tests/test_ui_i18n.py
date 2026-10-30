"""No Streamlit dependency: protect the complete presentation dictionary."""
from financial_adviser.ui_i18n import TEXT, category_label, canonical_category, t
import pytest


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_every_language_has_exactly_the_same_keys(lang):
    assert set(TEXT[lang]) == set(TEXT["fr"])
    assert set(TEXT[lang]["life_categories"]) == set(TEXT["fr"]["life_categories"])
    for key, value in TEXT[lang].items():
        if key == "life_categories":
            assert all(isinstance(s, str) and s.strip() for s in value.values())
        else:
            assert isinstance(value, str) and value.strip(), (lang, key)


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_parameterized_strings_render(lang):
    assert "2" in t(lang, "auto_assumptions", inflation="2", ret="5", growth="3")
    assert "2026" in t(lang, "sources_checked", date="2026-10-30")
    assert "1" in t(lang, "life_event", index=1)
    assert "fr" not in category_label(lang, "child").lower() if lang == "vi" else True


def test_translation_never_falls_back_to_another_language():
    with pytest.raises(KeyError):
        t("en", "__missing_key__")
    with pytest.raises(ValueError):
        t("xx", "income")


def test_legacy_categories_remain_importable():
    assert canonical_category("Child / Dependent") == "child"
    assert canonical_category("Health / Care") == "health"
    assert canonical_category("unemployment") == "unemployment"
    assert canonical_category("unknown") == "other"