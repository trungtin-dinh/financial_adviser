"""Financial Adviser — responsive multipage Streamlit application."""
import streamlit as st
from financial_adviser.ui_i18n import t

st.set_page_config(page_title="Financial Adviser", page_icon="📈", layout="wide", initial_sidebar_state="auto")

if st.session_state.get("language_choice") not in ("fr", "en", "vi"):
    requested_language = st.query_params.get("lang", "fr")
    st.session_state.language_choice = requested_language if requested_language in ("fr", "en", "vi") else "fr"

if st.session_state.get("language_choice") not in ("fr", "en", "vi"):
    st.session_state.language_choice = "fr"

with st.sidebar:
    st.title("📈 Financial Adviser")
    lang = st.selectbox(t(st.session_state.language_choice, "language"),
                        ["fr", "en", "vi"], key="language_choice",
                        format_func=lambda code: {"fr": "Français", "en": "English", "vi": "Tiếng Việt"}[code])
    st.caption(t(lang, "privacy"))

page = st.navigation([
    st.Page("pages/planning.py", title=t(lang, "nav_plan"), icon=":material/finance:", default=True),
    st.Page("pages/guide.py", title=t(lang, "nav_guide"), icon=":material/menu_book:"),
    st.Page("pages/sources.py", title=t(lang, "nav_sources"), icon=":material/public:"),
])
page.run()