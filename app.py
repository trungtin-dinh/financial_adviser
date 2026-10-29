"""Financial Adviser — simple multipage entrypoint. Run with streamlit run app.py."""
import streamlit as st

st.set_page_config(page_title="Financial Adviser", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
page = st.navigation([
    st.Page("pages/planning.py", title="Plan & Simulations", icon=":material/finance:", default=True),
    st.Page("pages/guide.py", title="Guide & Models", icon=":material/menu_book:"),
    st.Page("pages/sources.py", title="Sources & Regulations", icon=":material/public:"),
])
page.run()
