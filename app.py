"""Financial Adviser — responsive multipage Streamlit application."""
import streamlit as st
# Streamlit Community Cloud can rerun app.py while keeping an older imported module
# in the same Python process. Reload the local catalogue before constructing
# navigation, so new page keys are not missing after a hot deployment.
from importlib import reload
import financial_adviser.ui_i18n as ui_i18n
reload(ui_i18n)
t = ui_i18n.t

st.set_page_config(page_title="Financial Adviser", page_icon="📈", layout="wide", initial_sidebar_state="auto")

if st.session_state.get("language_choice") not in ("fr", "en", "vi"):
    requested_language = st.query_params.get("lang", "fr")
    st.session_state.language_choice = requested_language if requested_language in ("fr", "en", "vi") else "fr"

if st.session_state.get("language_choice") not in ("fr", "en", "vi"):
    st.session_state.language_choice = "fr"

lang = st.selectbox(
    t(st.session_state.language_choice, "language"),
    ["fr", "en", "vi"], key="language_choice",
    format_func=lambda code: {"fr": "Français", "en": "English", "vi": "Tiếng Việt"}[code],
    width=240,
)
with st.sidebar:
    st.title("📈 Financial Adviser")
    st.caption(t(lang, "privacy"))

page = st.navigation([
    st.Page("pages/planning.py", title=t(lang, "nav_plan"), icon=":material/finance:", default=True),
    st.Page("pages/benchmarks.py", title=t(lang, "nav_benchmarks"), icon=":material/monitoring:"),
    st.Page("pages/guide.py", title=t(lang, "nav_guide"), icon=":material/menu_book:"),
    st.Page("pages/sources.py", title=t(lang, "nav_sources"), icon=":material/public:"),
])
page.run()