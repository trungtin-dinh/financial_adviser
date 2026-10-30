"""Compact monthly cash-flow calendar on the saved results dashboard."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from financial_adviser.cashflow import monthly_cashflow_calendar
from financial_adviser.models import Plan


@st.fragment
def render_cashflow_calendar(plan: Plan, projection: pd.DataFrame, T, money) -> None:
    """Explore one calendar year without recalculating the financial engine."""
    with st.expander(T("cashflow_title"), expanded=False):
        st.caption(T("cashflow_intro"))
        schedule = monthly_cashflow_calendar(plan, projection)
        years = list(range(plan.start_year, plan.start_year + plan.years))
        if st.session_state.get("cashflow_selected_year") not in (None, *years):
            st.session_state.pop("cashflow_selected_year", None)
        selected_year = st.selectbox(
            T("cashflow_year"), years,
            key="cashflow_selected_year",
        )
        window = schedule.loc[schedule["year"] == selected_year]
        a, b, c = st.columns(3, wrap=True)
        a.metric(T("cashflow_net"), money(
            float(window["net_cashflow_before_returns"].sum()), plan.currency,
        ))
        b.metric(T("cashflow_min_cash"), money(
            float(window["cash"].min()), plan.currency,
        ))
        c.metric(T("cashflow_negative_months"), str(int((window["cash"] < 0).sum())))
        columns = {
            "period": "cashflow_period",
            "income": "cashflow_income",
            "expenses": "cashflow_expenses",
            "loan_payment": "cashflow_loan",
            "one_off": "cashflow_events",
            "investment_transfer": "cashflow_transfer",
            "net_cashflow_before_returns": "cashflow_flow",
            "cash": "cashflow_cash",
        }
        display = pd.DataFrame({
            T(label): (
                window[key].tolist() if key == "period"
                else [money(float(amount), plan.currency) for amount in window[key]]
            )
            for key, label in columns.items()
        })
        st.dataframe(display, hide_index=True, width="stretch")
        st.caption(T("cashflow_note"))
