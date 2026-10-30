"""Read-only and interactive result components for the planning page.

UI only: business rules and simulations remain in the existing engine modules.
Translations and currency formatting are passed in from the calling page to
preserve the selected language and all current formatting conventions.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from financial_adviser.charts import (
    DEFAULT_WEALTH_SERIES, WEALTH_SERIES, event_markers, household_figure,
    overlay_event_markers, resilience_figure, uncertainty_figure, wealth_figure,
)
from financial_adviser.insights import summarize_projection
from financial_adviser.models import Plan
from financial_adviser.resilience import analyze_liquidity


def reset_wealth_curves() -> None:
    """Return to the simple two-curve default on explicit request."""
    for field in WEALTH_SERIES:
        st.session_state["chart_curve_" + field] = field in DEFAULT_WEALTH_SERIES


@st.fragment
def render_result_charts(q: Plan, df: pd.DataFrame, mc: object | None, T, money) -> None:
    """Update chart options without rerunning the financial simulations."""
    views = ["wealth"]
    if q.children or q.adults or q.dependents:
        views.append("household")
    if mc is not None:
        views.append("uncertainty")
    if st.session_state.get("result_chart_view") not in (None, *views):
        st.session_state.pop("result_chart_view", None)
    selected_view = st.segmented_control(
        T("chart_view"), views, default="wealth", required=True,
        format_func=lambda option: T("chart_view_" + option),
        key="result_chart_view", width="stretch",
    )
    if selected_view == "wealth":
        with st.popover("☷ " + T("chart_curves"), width="stretch"):
            st.caption(T("chart_curves_help"))
            selected = [
                field for field in WEALTH_SERIES
                if st.checkbox(
                    T({
                        "net_worth": "net_worth",
                        "net_worth_real": "net_worth_real",
                        "cash": "cash_name",
                        "investments": "investments_name",
                        "loan_balance": "loan_name",
                        "property_value": "patrimony_property",
                        "other_assets": "patrimony_other",
                        "goal_nominal": "target_name",
                        "goal_real": "chart_goal_real",
                    }[field]),
                    value=field in DEFAULT_WEALTH_SERIES,
                    key="chart_curve_" + field,
                )
            ]
            st.button(
                T("chart_reset"), on_click=reset_wealth_curves,
                key="chart_reset_curves", width="stretch",
            )
        markers = event_markers(q)
        show_events = (
            st.checkbox(
                T("chart_events_toggle"), key="chart_show_events",
                value=False, help=T("chart_events_help"),
            )
            if markers else False
        )
        if selected:
            fig = wealth_figure(df, q.goal, q.start_year, q.currency, selected, T)
            if show_events:
                drawn, total = overlay_event_markers(fig, markers)
            st.plotly_chart(fig, width="stretch", key="financial_wealth_chart",
                            config={"displaylogo": False, "scrollZoom": False})
            if show_events:
                st.caption(T("chart_event_lines"))
                if total > drawn:
                    st.caption(T("chart_event_marker_limit", count=total - drawn))
                with st.expander(T("chart_event_list"), expanded=False):
                    kinds = {
                        "event_start": "chart_event_start",
                        "event_end": "chart_event_end",
                        "oneoff": "chart_event_oneoff",
                        "child_arrival": "chart_event_child_arrival",
                        "child_support_end": "chart_event_child_support_end",
                        "dependent_start": "chart_event_dependent_start",
                        "dependent_end": "chart_event_dependent_end",
                        "retirement": "chart_event_retirement",
                    }
                    event_rows = []
                    for mark in markers:
                        year = q.start_year + (mark.month - 1) // 12
                        month = (mark.month - 1) % 12 + 1
                        event_rows.append({
                            T("chart_event_date"): f"{year}-{month:02d}",
                            T("chart_event_type"): T(kinds[mark.kind]),
                            T("chart_event_label"): mark.label or T(kinds[mark.kind]),
                        })
                    st.dataframe(pd.DataFrame(event_rows), hide_index=True, width="stretch")
        else:
            st.info(T("chart_select_one"))
        st.caption(T("chart_goal_comparison"))
    elif selected_view == "household":
        st.caption(T("chart_household_signed"))
        fig = household_figure(df, q.start_year, q.currency, T)
        if len(fig.data):
            st.plotly_chart(fig, width="stretch", key="financial_household_chart",
                            config={"displaylogo": False, "scrollZoom": False})
        else:
            st.info(T("chart_household_no_change"))
        if q.children:
            st.caption(T("household_total_child", value=money(
                float(df.child_expenses.sum()), q.currency)))
    elif selected_view == "uncertainty" and mc is not None:
        st.caption(T("mc_hint", paths=mc.sample_paths, seed=mc.seed))
        st.plotly_chart(
            uncertainty_figure(df, mc, q.start_year, q.currency, T),
            width="stretch", key="financial_uncertainty_chart",
            config={"displaylogo": False, "scrollZoom": False},
        )
        a, b = st.columns(2, wrap=True)
        a.metric(T("goal_probability"),
                 f"{mc.probability_goal:.1%}" if q.goal > 0 else T("not_applicable"))
        b.metric(T("chart_min_cash"), money(float(df.cash.min()), q.currency))
        st.caption(T("chart_mc_cash_note"))





def render_financial_overview(plan: Plan, df: pd.DataFrame, T, money) -> None:
    """Read-only, plain-language summary of the LAST calculated scenario."""
    facts = summarize_projection(plan, df)
    st.markdown("#### " + T("summary_title"))
    st.caption(T("summary_intro"))

    if facts.first_deficit_month is None:
        minimum_cash = money(float(df.cash.min()), plan.currency)
        liquidity = T("summary_liquidity_nonnegative", minimum=minimum_cash)
    else:
        month = facts.first_deficit_month
        date = f"{plan.start_year + (month - 1) // 12}-{(month - 1) % 12 + 1:02d}"
        liquidity = T(
            "summary_liquidity_negative", date=date,
            months=facts.negative_cash_months,
            funding=money(facts.funding_gap, plan.currency),
        )
    st.markdown("**" + T("summary_liquidity_label") + "** — " + liquidity)

    margin = facts.first_month_regular_balance
    if margin < 0:
        regular = T("summary_margin_negative", value=money(abs(margin), plan.currency))
    elif margin > 0:
        regular = T("summary_margin_positive", value=money(margin, plan.currency))
    else:
        regular = T("summary_margin_balanced")
    st.markdown("**" + T("summary_margin_label") + "** — " + regular)

    if not facts.goal_is_specified:
        goal_text = T("summary_goal_zero")
    elif facts.nominal_goal_reached:
        goal_text = T("summary_goal_reached",
                      value=money(facts.final_nominal_wealth, plan.currency))
    else:
        goal_text = T("summary_goal_not_reached",
                      gap=money(facts.nominal_goal_gap, plan.currency))
    if facts.nominal_goal_reached and facts.first_deficit_month is not None:
        goal_text += " " + T("summary_goal_liquidity_warning")
    st.markdown("**" + T("summary_goal_label") + "** — " + goal_text)

    purchasing = T(
        "summary_purchasing",
        nominal=money(facts.final_nominal_wealth, plan.currency),
        real=money(facts.final_real_wealth, plan.currency),
        inflation=f"{facts.inflation_pct:g}",
    )
    st.markdown("**" + T("summary_purchasing_label") + "** — " + purchasing)
    with st.expander(T("summary_method_title"), expanded=False):
        st.markdown(T("summary_method"))
    st.caption(T("summary_disclaimer"))


@st.fragment
def render_resilience_panel(plan: Plan, df: pd.DataFrame, T, money) -> None:
    """Optional cash-only what-if: rerender without running the main engine."""
    with st.expander(T("resilience_title"), expanded=False):
        st.caption(T("resilience_intro"))
        if st.session_state.get("_resilience_source") != plan:
            st.session_state.pop("resilience_shock_month", None)
            st.session_state.pop("resilience_expense_amount", None)
            st.session_state["_resilience_source"] = plan
        baseline = analyze_liquidity(plan, df)
        a, b = st.columns(2, wrap=True)
        a.metric(T("resilience_baseline_gap"),
                 money(baseline.baseline_funding_gap, plan.currency))
        if baseline.baseline_first_deficit_month is None:
            first_baseline = T("not_applicable")
        else:
            month = baseline.baseline_first_deficit_month
            first_baseline = f"{plan.start_year + (month - 1) // 12}-{(month - 1) % 12 + 1:02d}"
        b.metric(T("resilience_first_deficit"), first_baseline)
        st.caption(T("resilience_initial_buffer_help"))
        left, right = st.columns(2, wrap=True)
        with left:
            shock_month = st.number_input(
                T("resilience_month"), min_value=1, max_value=plan.years * 12,
                value=1, step=1, key="resilience_shock_month",
                help=T("resilience_month_help"),
            )
        with right:
            shock_amount = st.number_input(
                T("resilience_amount"), min_value=0.0, value=0.0,
                step=1_000_000.0 if plan.currency == "VND" else 100.0,
                key="resilience_expense_amount",
            )
        try:
            test = analyze_liquidity(
                plan, df, shock_month=int(shock_month),
                shock_amount=float(shock_amount),
            )
        except (ValueError, OverflowError):
            st.error(T("resilience_invalid"))
            return
        a, b = st.columns(2, wrap=True)
        a.metric(T("resilience_capacity"),
                 money(test.maximum_absorbable_expense, plan.currency),
                 help=T("resilience_capacity_help"))
        b.metric(T("resilience_test_gap"),
                 money(test.shock_funding_gap, plan.currency))
        if test.baseline_funding_gap > 0:
            st.warning(T("resilience_baseline_deficit"))
        elif test.shock_amount == 0:
            st.info(T("resilience_select_amount"))
        elif test.shock_first_deficit_month is not None:
            first = test.shock_first_deficit_month
            date = f"{plan.start_year + (first - 1) // 12}-{(first - 1) % 12 + 1:02d}"
            st.warning(T("resilience_shock_deficit",
                         date=date, count=test.shock_deficit_months))
        else:
            st.info(T("resilience_no_simulated_deficit"))
        st.plotly_chart(
            resilience_figure(df, test, plan.start_year, plan.currency, T),
            width="stretch", key="cash_resilience_chart",
            config={"displaylogo": False, "scrollZoom": False},
        )
        st.caption(T("resilience_chart_note"))
        st.caption(T("resilience_disclaimer"))
