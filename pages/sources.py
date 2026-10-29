"""Economic data and regulatory references: inspect sources, no automatic legal changes."""
import json
from pathlib import Path
import streamlit as st
from financial_adviser.i18n import tr
from financial_adviser.models import Plan
from dataclasses import replace
from financial_adviser.sources import WB_DOC, fetch_recent_inflation

ROOT = Path(__file__).resolve().parent.parent
lang = st.session_state.get("language_choice", "fr")
st.title("🔄 " + tr(lang, "sources"))
st.info("Historical inflation is NOT a prediction. Tax and regulatory texts are referenced only, never auto-executed.")
@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_inflation(country: str) -> dict:
    try:
        return {"data": fetch_recent_inflation(country), "error": ""}
    except (OSError, ValueError, RuntimeError) as exc:
        return {"data": None, "error": str(exc)}
if "plan" not in st.session_state:
    st.session_state.plan = Plan()
auto = st.checkbox("Retrieve historical observed inflation (24h cache)", value=False)
if st.button("🔄 " + tr(lang, "refresh")):
    cached_inflation.clear()
    auto = True
if auto:
    lookup = cached_inflation(st.session_state.plan.country)
    if lookup["data"] is None:
        st.warning("Source unavailable; no assumptions changed. " + lookup["error"][:250])
    else:
        observation = lookup["data"]
        st.metric(f"World Bank CPI annual inflation — {observation['observation_year']}", f"{observation['value_pct']:.2f}%")
        st.caption(f"Retrieved {observation['retrieved_at']} UTC. Historical observation only.")
        st.link_button("Official source", observation["source_url"])
        if st.button("Use this historical value as my scenario assumption (manual choice)"):
            st.session_state.plan = replace(st.session_state.plan, inflation_pct=observation["value_pct"])
            st.session_state.result = None
            st.rerun()
st.markdown(f"[World Bank API methodology]({WB_DOC})")
st.divider()
catalogue = json.loads((ROOT / "rules" / "catalogue.json").read_text(encoding="utf-8"))
st.caption(f"Catalog last checked {catalogue['checked_on']}. No automated legal extraction or tax calculation.")
for entry in catalogue["entries"]:
    with st.expander(f"{entry['country']} · {entry['id']} · {entry['status']}"):
        st.write(entry["notes"])
        st.write(f"Effective from: {entry['effective_from']}")
        st.link_button("Official legal source", entry["source_url"])
st.warning("Verify official law before decisions. Catalog references are not exhaustive.")
