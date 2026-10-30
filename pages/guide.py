"""Reference documents: full French sources, with complete localized navigation."""
from pathlib import Path
import streamlit as st
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parent.parent
lang = st.session_state.get("language_choice", "fr")
st.title("📖 " + t(lang, "nav_guide"))
st.caption(t(lang, "guide_caption") if lang == "fr" else t(lang, "guide_language_note"))

DOCS = [
    ("01_CAHIER_DES_CHARGES.md", "guide_requirements"),
    ("02_MODELES_MATHEMATIQUES.md", "guide_math"),
    ("03_SOURCES_ET_REGLES.md", "guide_provenance"),
    ("04_ARCHITECTURE.md", "guide_arch"),
    ("05_BENCHMARK.md", "guide_bench"),
    ("06_QUALITE_ET_LIMITES.md", "guide_limits"),
    ("07_ROADMAP.md", "guide_roadmap"),
    ("08_JOURNAL.md", "guide_journal"),
    ("09_FACTEURS_DE_VIE_ET_UX.md", "guide_life"),
    ("17_FACTEURS_FINANCIERS_SOCIAUX_ET_RISQUES.md", "guide_risk_factors"),
    ("18_PROTOCOL_EVALUATIONS_HUMAINES.md", "guide_research"),
]
if lang == "fr":
    for filename, key in DOCS:
        with st.expander(t(lang, key), expanded=False):
            st.markdown((ROOT / "Documentation" / filename).read_text(encoding="utf-8"))
else:
    st.info(t(lang, "guide_summary"))
    for filename, key in DOCS:
        st.link_button(t(lang, key),
                       f"https://github.com/trungtin-dinh/financial_adviser/blob/main/Documentation/{filename}",
                       width="stretch")
st.link_button(t(lang, "guide_link"), "https://github.com/trungtin-dinh/financial_adviser/tree/main/Documentation")