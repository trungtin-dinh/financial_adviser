"""Browsable documentation isolated from the financial input forms."""
from pathlib import Path
import streamlit as st
from financial_adviser.i18n import tr

ROOT = Path(__file__).resolve().parent.parent
lang = st.session_state.get("language_choice", "fr")
st.title("📖 " + tr(lang, "docs"))
st.caption("The complete and versioned technical documentation remains in the GitHub Documentation/ folder.")
for name, label in [
    ("01_CAHIER_DES_CHARGES.md", "Requirements / Cahier des charges"),
    ("02_MODELES_MATHEMATIQUES.md", "Mathematical models / Équations"),
    ("03_SOURCES_ET_REGLES.md", "Source provenance / Sources officielles"),
    ("04_ARCHITECTURE.md", "Architecture"),
    ("05_BENCHMARK.md", "Existing software / Étude comparative"),
    ("06_QUALITE_ET_LIMITES.md", "Limitations & privacy / Limites"),
    ("07_ROADMAP.md", "Roadmap / Feuille de route"),
    ("08_JOURNAL.md", "Decisions / Journal"),
    ("09_FACTEURS_DE_VIE_ET_UX.md", "Life events, goals & user review / Événements et UX"),
]:
    with st.expander(label, expanded=False):
        st.markdown((ROOT / "Documentation" / name).read_text(encoding="utf-8"))
st.link_button("Open full repository documentation", "https://github.com/trungtin-dinh/financial_adviser/tree/main/Documentation")
