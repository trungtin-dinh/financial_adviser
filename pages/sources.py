"""Official economic and legal references, without automated regulatory execution."""
import json
from dataclasses import replace
from pathlib import Path
import streamlit as st
from financial_adviser.ui_i18n import t
from financial_adviser.models import Plan
from financial_adviser.sources import WB_DOC, fetch_recent_inflation

ROOT = Path(__file__).resolve().parent.parent
lang = st.session_state.get("language_choice", "fr")
st.title("🔄 " + t(lang, "nav_sources"))
st.info(t(lang, "sources_info"))

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_inflation(country: str) -> dict:
    try:
        return {"data": fetch_recent_inflation(country), "error": ""}
    except (OSError, ValueError, RuntimeError):
        return {"data": None, "error": "unavailable"}

if "plan" not in st.session_state:
    st.session_state.plan = Plan()
if "result" not in st.session_state:
    st.session_state.result = None
retrieve = st.checkbox(t(lang, "sources_optin"), value=False)
if st.button("🔄 " + t(lang, "sources_refresh")):
    cached_inflation.clear()
    retrieve = True
if retrieve:
    observation = cached_inflation(st.session_state.plan.country)["data"]
    if observation is None:
        st.warning(t(lang, "sources_unavailable"))
    else:
        st.metric(f"{t(lang, 'sources_observed')} — {observation['observation_year']}",
                  f"{observation['value_pct']:.2f}%")
        st.caption(t(lang, "sources_retrieved", date=observation["retrieved_at"]))
        st.link_button(t(lang, "sources_official"), observation["source_url"])
        if st.button(t(lang, "sources_use")):
            st.session_state.plan = replace(st.session_state.plan, inflation_pct=observation["value_pct"])
            st.session_state.result = None
            st.session_state.pop("goal_alternatives", None)
            st.session_state.pop("input_inflation", None)
            st.rerun()
st.link_button(t(lang, "sources_method"), WB_DOC)
st.divider()
catalogue = json.loads((ROOT / "rules" / "catalogue.json").read_text(encoding="utf-8"))
st.caption(t(lang, "sources_checked", date=catalogue["checked_on"]))
for entry in catalogue["entries"]:
    key = {"livret_a_2026_08": "source_livret", "pit_law_109_2025": "source_tax"}.get(entry["id"])
    if key is None:
        continue
    with st.expander(f"{entry['country']} · {t(lang, key)}"):
        st.write(t(lang, key + "_note"))
        st.write(f"{t(lang, 'sources_since')}: {entry['effective_from']}")
        st.caption(t(lang, "sources_status"))
        st.link_button(t(lang, "sources_official"), entry["source_url"])
st.warning(t(lang, "sources_warning"))