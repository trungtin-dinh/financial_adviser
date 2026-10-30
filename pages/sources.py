"""Legal reference inventory; live statistical observations live on their own page."""
from pathlib import Path
import json
import streamlit as st
from financial_adviser.ui_i18n import t

ROOT = Path(__file__).resolve().parent.parent
lang = st.session_state.get("language_choice", "fr")
st.title("🔄 " + t(lang, "nav_sources"))
st.info(t(lang, "sources_info"))
if st.button(t(lang, "nav_benchmarks"), width="stretch"):
    st.switch_page("pages/benchmarks.py")
st.divider()
catalogue = json.loads((ROOT / "rules" / "catalogue.json").read_text(encoding="utf-8"))
st.caption(t(lang, "sources_checked", date=catalogue["checked_on"]))
for entry in catalogue["entries"]:
    key = {"livret_a_2026_08": "source_livret", "pit_law_109_2025": "source_tax"}.get(entry["id"])
    if key is None:
        continue
    with st.expander(f"{entry['country']} · {t(lang,key)}"):
        st.write(t(lang, key + "_note"))
        st.write(f"{t(lang,'sources_since')}: {entry['effective_from']}")
        st.caption(t(lang, "sources_status"))
        st.link_button(t(lang,"sources_official"),entry["source_url"])
st.warning(t(lang,"sources_warning"))
