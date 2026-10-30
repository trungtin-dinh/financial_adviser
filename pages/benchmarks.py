"""Curated demographic references and opt-in historical inflation scenario preset."""

from __future__ import annotations

import streamlit as st

from financial_adviser.benchmark_i18n import b
from financial_adviser.models import Plan
from financial_adviser.sources import fetch_recent_inflation
from financial_adviser.statistical_references import (
    can_autofill,
    confirmed_inflation_update,
    load_references,
)

lang = st.session_state.get("language_choice", "fr")
B = lambda key, **kwargs: b(lang, key, **kwargs)

if "plan" not in st.session_state:
    st.session_state.plan = Plan()

plan = st.session_state.plan
country = plan.country
st.title("📊 " + B("title"))
st.caption(B("intro"))
st.warning(B("stale"))

st.subheader(B("curated"))
st.caption(B("snapshot", date="2026-10-30"))
for point in load_references(country):
    with st.container(border=True):
        st.markdown("**" + B(point.id) + "**")
        full = f"{point.value:,.0f}".replace(",", " ")
        if point.currency == "VND" and point.value >= 1_000_000:
            numeral = f"{point.value / 1_000_000:.1f}".replace(".", "," if lang in ("fr", "vi") else ".") + " M ₫"
        else:
            numeral = full + " €"
        if point.precision.startswith("approximate"):
            numeral = "≈ " + numeral
        st.metric(B("statistics"), numeral)
        st.caption(f"{full} {point.currency} · {B('unit_month')}")
        st.caption(f"{B(point.statistic)} · {B('period')}: {point.observed_year} · {B('publication')}: {point.published_on}")
        st.write(B(point.id + "_desc"))
        if point.precision.startswith("approximate"):
            st.caption(B("approx"))
        if not can_autofill(point, "monthly_income") and not can_autofill(point, "monthly_expenses"):
            st.caption(B("not_compatible"))
        st.link_button(B("source"), point.source_url)

st.info(B("no_autofill"))
st.divider()

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def recent_inflation(country_code: str) -> dict:
    """Observation-only cache; manual refresh invalidates it without changing a plan."""
    return fetch_recent_inflation(country_code)

st.subheader(B("inflation_title"))
st.caption(B("inflation_intro"))
st.caption(B("unsaved"))
if st.session_state.get("benchmark_country") != country:
    st.session_state.benchmark_country = country
    st.session_state.pop("benchmark_observation", None)

if st.button("🔄 " + B("fetch"), width="stretch"):
    try:
        recent_inflation.clear()
        st.session_state.benchmark_observation = recent_inflation(country)
    except (OSError, RuntimeError, ValueError, KeyError):
        st.session_state.pop("benchmark_observation", None)
        st.warning(B("fetch_failed"))

observation = st.session_state.get("benchmark_observation")
if observation is not None and observation.get("country") == country:
    with st.container(border=True):
        st.markdown("**" + B("preview") + "**")
        left, right = st.columns(2, wrap=True)
        left.metric(B("current"), f"{plan.inflation_pct:.2f}%")
        right.metric(B("proposed"), f"{float(observation['value_pct']):.2f}%")
        st.caption(B("observed", year=observation["observation_year"]))
        st.link_button(B("source"), observation["source_url"])
        agree = st.checkbox(B("confirmation"), value=False, key=f"benchmark_confirm_{country}_{observation['observation_year']}_{observation['value_pct']}")
        if st.button(B("apply"), type="primary", disabled=not agree, width="stretch"):
            try:
                updated = confirmed_inflation_update(plan, observation, consent=agree)
            except (ValueError, PermissionError, TypeError):
                st.error(B("invalid"))
            else:
                st.session_state.plan = updated
                st.session_state.result = None
                st.session_state.pop("goal_alternatives", None)
                st.session_state.pop("goal_query", None)
                st.session_state.pop("field_inflation", None)
                st.success(B("applied"))

if st.button("← " + B("back"), width="stretch"):
    st.switch_page("pages/planning.py")
