"""User-facing documentation, separate from internal technical notes."""
from pathlib import Path
import re

import streamlit as st

from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "Documentation" / "public"
LANG = st.session_state.get("language_choice", "fr")

SECTION_KEYS = (
    "guide_requirements", "guide_math", "guide_provenance",
    "guide_arch", "guide_bench", "guide_limits", "guide_roadmap",
    "guide_journal", "guide_life", "guide_risk_factors",
    "guide_research", "guide_household",
)


def load_public_sections(language: str) -> list[str]:
    """Read the reviewed user-facing sections in their display order."""
    if language not in ("fr", "en", "vi"):
        raise ValueError("Unsupported guide language")
    markdown = (PUBLIC_DIR / f"guide_{language}.md").read_text(encoding="utf-8")
    # Numbered headings remain readable on GitHub; the Streamlit page shows
    # each section inside a separate, localized expandable panel.
    parts = re.split(r"(?m)^## \d{1,2}\. [^\n]+\n", markdown)
    sections = [part.strip() for part in parts[1:]]
    if len(sections) != len(SECTION_KEYS) or any(not part for part in sections):
        raise ValueError("Invalid public guide section structure")
    return sections


st.title("📖 " + t(LANG, "nav_guide"))
st.caption(t(LANG, "guide_caption"))

for key, body in zip(SECTION_KEYS, load_public_sections(LANG)):
    with st.expander(t(LANG, key), expanded=(key == SECTION_KEYS[0])):
        st.markdown(body)

st.link_button(
    t(LANG, "guide_link"),
    "https://github.com/trungtin-dinh/financial_adviser/blob/main/"
    f"Documentation/public/guide_{LANG}.md",
)
