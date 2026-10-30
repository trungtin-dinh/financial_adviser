"""Financial Adviser — responsive multipage Streamlit application."""
import ast
import importlib
from pathlib import Path
import sys

import streamlit as st
import financial_adviser as pkg

# Streamlit's long-lived worker can keep old imported Python modules during
# Community Cloud hot deployments. Compare source version on disk to the
# already imported package, then reload dependent modules in dependency order.
# The planning page also migrates existing session-state Plan objects.
disk_version_line = next(
    line for line in (Path(__file__).parent / "financial_adviser" / "__init__.py")
    .read_text(encoding="utf-8").splitlines()
    if line.startswith("__version__ = ")
)
disk_version = ast.literal_eval(disk_version_line.split("=", 1)[1].strip())
if pkg.__version__ != disk_version:
    importlib.reload(pkg)
    for module in (
        "financial_adviser.households",
        "financial_adviser.models",
        "financial_adviser.engine",
        "financial_adviser.scenarios",
        "financial_adviser.io",
        "financial_adviser.session_compat",
        "financial_adviser.household_ui",
        "financial_adviser.statistical_references",
        "financial_adviser.benchmark_i18n",
    ):
        if module in sys.modules:
            importlib.reload(sys.modules[module])
import financial_adviser.ui_i18n as ui_i18n
importlib.reload(ui_i18n)
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