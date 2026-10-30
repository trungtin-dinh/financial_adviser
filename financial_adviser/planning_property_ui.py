"""Small localized editor for one future, explicitly financed property purchase."""
from __future__ import annotations

import streamlit as st

from financial_adviser.models import Plan, PropertyPurchase


def render_property_purchase(plan: Plan, years: int, T, step: float, money) -> PropertyPurchase | None:
    """Collect one closing transaction; never infer a property from existing debt."""
    purchase = plan.property_purchase
    with st.expander("🏡 " + T("purchase_title"), expanded=False):
        st.caption(T("purchase_intro"))
        enabled = st.checkbox(
            T("purchase_enable"), value=purchase is not None,
            key="field_purchase_enabled",
        )
        if not enabled:
            return None
        a, b = st.columns(2, wrap=True)
        with a:
            month = st.number_input(
                T("purchase_month"), min_value=1, max_value=years * 12,
                value=purchase.month if purchase is not None else min(years * 12, 13),
                step=1, key="field_purchase_month",
            )
            price = st.number_input(
                T("purchase_price"), min_value=1.0,
                value=float(purchase.price) if purchase is not None
                else (3_000_000_000.0 if plan.currency == "VND" else 200_000.0),
                step=step * 10, key="field_purchase_price",
            )
            down = st.number_input(
                T("purchase_down"), min_value=0.0,
                value=float(purchase.down_payment) if purchase is not None
                else (600_000_000.0 if plan.currency == "VND" else 40_000.0),
                step=step * 10, key="field_purchase_down",
            )
        with b:
            fees = st.number_input(
                T("purchase_fees"), min_value=0.0,
                value=float(purchase.fees) if purchase is not None
                else (60_000_000.0 if plan.currency == "VND" else 10_000.0),
                step=step * 10, key="field_purchase_fees",
            )
            apr = st.number_input(
                T("purchase_apr"), min_value=0.0, max_value=100.0,
                value=float(purchase.loan_apr_pct) if purchase is not None else 3.5,
                step=0.25, key="field_purchase_apr",
            )
            term = st.number_input(
                T("purchase_years"), min_value=1, max_value=60,
                value=purchase.loan_years if purchase is not None else 20,
                step=1, key="field_purchase_years",
            )
        if down > price:
            st.warning(T("purchase_invalid"))
        st.caption(T("purchase_summary", payment=money(down + fees, plan.currency),
                     mortgage=money(max(0., price - down), plan.currency)))
        st.caption(T("purchase_no_double_count"))
        return PropertyPurchase(
            month=int(month), price=float(price), down_payment=float(down),
            fees=float(fees), loan_apr_pct=float(apr), loan_years=int(term),
        )
