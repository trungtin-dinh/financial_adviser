"""Custom comparison editor and read-only result presentation.

The financial comparisons are provided by the existing engine. Locale-specific
rendering is injected by the active Streamlit page.
"""
from __future__ import annotations

import hashlib
import json

import pandas as pd
import streamlit as st

from financial_adviser.charts import custom_comparison_figure
from financial_adviser.custom_comparison import (
    CUSTOM_AMOUNT_FIELDS, CUSTOM_RATE_FIELDS, CUSTOM_INTEGER_FIELDS,
    compare_custom_scenarios, make_custom_variant,
)
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import Plan


def remember_custom_mode() -> None:
    """Retain custom-edit vs JSON-import mode across lazy tab switches."""
    st.session_state["_last_custom_input_mode"] = st.session_state["custom_input_mode"]


def render_custom_comparison(base: Plan, years: int, T, money) -> None:
    """Edit or import a second complete scenario, with explicit comparison."""
    with st.container():
        st.subheader(T("custom_title"))
        st.caption(T("custom_intro"))
        if st.session_state.get("_custom_form_source") != base:
            for field in (*CUSTOM_AMOUNT_FIELDS, *CUSTOM_RATE_FIELDS,
                          *CUSTOM_INTEGER_FIELDS):
                st.session_state.pop("custom_field_" + field, None)
            st.session_state.pop("custom_input_mode", None)
            st.session_state.pop("_last_custom_input_mode", None)
            st.session_state.pop("custom_import", None)
            st.session_state.pop("custom_metric", None)
            st.session_state.pop("_custom_comparison", None)
            st.session_state["_custom_form_source"] = base

        mode = st.radio(
            T("custom_mode"), ("edit", "import"),
            format_func=lambda x: T("custom_mode_" + x),
            index=1 if st.session_state.get("_last_custom_input_mode") == "import" else 0,
            horizontal=True, key="custom_input_mode",
            on_change=remember_custom_mode,
        )
        previous = st.session_state.get("_custom_comparison")
        if previous is not None and (
            previous["base"] != base or previous["years"] != years
            or previous["mode"] != mode
        ):
            previous = None
            st.session_state.pop("_custom_comparison", None)

        with st.form("custom_comparison_form"):
            variant_values = {}
            imported_file = None
            if mode == "edit":
                st.caption(T("custom_copy_help"))
                # A stored comparison must reopen with the inputs that actually
                # produced its visible chart, even after lazy tab unmounting.
                edit_source = (previous["result"].alternative_plan
                               if previous is not None and previous["mode"] == "edit"
                               else base)
                a, b = st.columns(2, wrap=True)
                for idx, field in enumerate(CUSTOM_AMOUNT_FIELDS):
                    with (a if idx % 2 == 0 else b):
                        variant_values[field] = st.number_input(
                            T("custom_field_" + field),
                            min_value=0.0,
                            value=float(getattr(edit_source, field)),
                            step=(1_000_000.0 if base.currency == "VND" else 100.0),
                            key="custom_field_" + field,
                        )
                with st.expander(T("custom_advanced"), expanded=False):
                    c, d = st.columns(2, wrap=True)
                    for idx, field in enumerate(CUSTOM_RATE_FIELDS):
                        with (c if idx % 2 == 0 else d):
                            lo = 0.0 if field == "loan_apr_pct" else -98.999999
                            hi = 100.0 if field == "loan_apr_pct" else 200.0
                            variant_values[field] = st.number_input(
                                T("custom_field_" + field),
                                min_value=lo, max_value=hi,
                                value=float(getattr(edit_source, field)),
                                step=0.5, key="custom_field_" + field,
                            )
                    variant_values["loan_years"] = int(st.number_input(
                        T("custom_field_loan_years"),
                        min_value=1, max_value=60,
                        value=int(edit_source.loan_years),
                        step=1, key="custom_field_loan_years",
                    ))
            else:
                st.caption(T("custom_import_help"))
                imported_file = st.file_uploader(
                    T("custom_file"), type=["json"], max_upload_size=1,
                    key="custom_import",
                )
            submitted = st.form_submit_button(
                T("custom_calculate"), width="stretch",
                key="custom_compare_submit",
            )

        upload_fingerprint = (
            hashlib.sha256(imported_file.getvalue()).hexdigest()
            if mode == "import" and imported_file is not None else None
        )
        if (mode == "import" and previous is not None
                and previous.get("upload_fingerprint") != upload_fingerprint):
            previous = None
            st.session_state.pop("_custom_comparison", None)

        if submitted:
            try:
                if mode == "edit":
                    alternative = make_custom_variant(base, variant_values)
                elif imported_file is not None:
                    alternative = load_plan(imported_file.getvalue())
                else:
                    raise ValueError("Missing comparison file")
                comparison = compare_custom_scenarios(
                    base, alternative, int(years))
            except (ValueError, KeyError, TypeError, UnicodeError,
                    json.JSONDecodeError, OverflowError):
                st.error(T("custom_invalid"))
                st.session_state.pop("_custom_comparison", None)
                previous = None
            else:
                previous = {
                    "base": base, "years": years,
                    "mode": mode, "result": comparison,
                    "upload_fingerprint": upload_fingerprint,
                }
                st.session_state["_custom_comparison"] = previous

        if previous is None:
            st.info(T("custom_prompt"))
            return

        comparison = previous["result"]
        metric = st.segmented_control(
            T("custom_display"), ("net_worth", "net_worth_real", "cash"),
            default="net_worth_real", required=True,
            format_func=lambda f: T("custom_plot_" + f),
            key="custom_metric", width="stretch",
        )
        st.plotly_chart(
            custom_comparison_figure(comparison, metric, base.currency, T),
            width="stretch", key="custom_comparison_chart",
            config={"displaylogo": False, "scrollZoom": False},
        )
        st.caption(T("custom_legend"))
        a, b, c = st.columns(3, wrap=True)
        a.metric(T("custom_diff_nominal"),
                 money(comparison.nominal_difference, base.currency))
        b.metric(T("custom_diff_real"),
                 money(comparison.real_difference, base.currency))
        c.metric(T("custom_diff_cash"),
                 money(comparison.minimum_cash_difference, base.currency))

        def goal_text(reached: bool | None) -> str:
            return T("not_applicable") if reached is None else (
                T("yes") if reached else T("no"))

        rows = []
        for name, df, deficit_months, funding_gap, reached in (
            (T("custom_reference"), comparison.reference,
             comparison.reference_deficit_months,
             comparison.reference_funding_gap,
             comparison.reference_goal_reached),
            (T("custom_variant"), comparison.alternative,
             comparison.alternative_deficit_months,
             comparison.alternative_funding_gap,
             comparison.alternative_goal_reached),
        ):
            rows.append({
                T("custom_col_scenario"): name,
                T("custom_col_nominal"): money(
                    float(df.net_worth.iloc[-1]), base.currency),
                T("custom_col_real"): money(
                    float(df.net_worth_real.iloc[-1]), base.currency),
                T("custom_col_min_cash"): money(
                    float(df.cash.min()), base.currency),
                T("custom_col_gap"): money(funding_gap, base.currency),
                T("custom_col_deficit_months"): deficit_months,
                T("custom_col_goal"): goal_text(reached),
            })
        with st.expander(T("custom_details"), expanded=False):
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        if (comparison.reference_deficit_months > 0
                or comparison.alternative_deficit_months > 0):
            st.warning(T("custom_cash_warning"))
        st.caption(T("custom_limitations"))
        st.download_button(
            T("custom_download"), data=dump_plan(comparison.alternative_plan),
            file_name="financial_adviser_variant.json",
            mime="application/json", width="stretch",
            key="custom_download_variant",
        )
