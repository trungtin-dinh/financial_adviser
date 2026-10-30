"""Alternative scenarios, sensitivity and stress-test interface.

Each expensive view stays lazy. Calculations are delegated to their existing
domain modules; locale and currency formatting come from the active page.
"""
from __future__ import annotations

from dataclasses import replace

import pandas as pd
import streamlit as st

from financial_adviser.charts import (
    assumption_sensitivity_figure, comparison_figure, stress_liquidity_figure,
)
from financial_adviser.comparisons import build_comparisons, minimum_comparison_years
from financial_adviser.models import Plan
from financial_adviser.planning_custom_ui import render_custom_comparison
from financial_adviser.scenarios import PRESET_IDS, evaluate_stresses
from financial_adviser.sensitivity import analyze_assumptions


def remember_analysis_view(T) -> None:
    """Preserve the selected analysis when lazy tabs are unmounted."""
    label = st.session_state.get("comparison_analysis_navigation")
    for name in ("variants", "custom", "sensitivity", "stress"):
        if label == T("analysis_" + name):
            st.session_state["_last_analysis_view"] = name
            break


@st.fragment
def render_comparison_tab(base: Plan, T, money) -> None:
    """Run aligned what-if simulations only when comparison settings change."""
    st.subheader(T("tab_compare"))
    st.caption(T("compare_intro"))
    minimum_years = minimum_comparison_years(base)
    if st.session_state.get("_comparison_source") != base:
        st.session_state.pop("comparison_horizon", None)
        st.session_state["_comparison_source"] = base
    horizon = st.number_input(
        T("compare_horizon"), min_value=minimum_years,
        max_value=60, value=base.years, step=1,
        help=T("compare_horizon_help"),
        key="comparison_horizon",
    )
    if minimum_years > 1:
        st.caption(T("compare_minimum_horizon", years=minimum_years))
    st.caption(T("compare_same_horizon", years=horizon,
                 final_year=base.start_year + horizon))
    st.caption(T("analysis_navigation_hint"))
    variant_view, custom_view, sensitivity_view, stress_view = st.tabs(
        [
            T("analysis_variants"), T("analysis_custom"),
            T("analysis_sensitivity"), T("analysis_stress"),
        ],
        key="comparison_analysis_navigation",
        default=T("analysis_" + st.session_state.get("_last_analysis_view", "variants")),
        on_change=remember_analysis_view, args=(T,),
    )
    if variant_view.open:
        with variant_view:
            shock = st.number_input(
                T("return_shock"), min_value=0.5, max_value=10.0,
                value=3.0, step=0.5, key="compare_return_shock",
            )
            comparisons = build_comparisons(base, int(horizon), float(shock))
            chart = comparison_figure(comparisons, base.start_year, base.currency,
                                      T, base.goal)
            st.plotly_chart(chart, width="stretch", key="aligned_scenario_comparison",
                            config={"displaylogo": False, "scrollZoom": False})
            with st.expander(T("compare_detailed_results"), expanded=False):
                rows = [{
                    T("scenario_col"): T(case.key),
                    T("return_col"): case.return_pct,
                    T("final_col"): money(case.terminal_nominal, base.currency),
                    T("compare_real_final"): money(case.terminal_real, base.currency),
                    T("compare_delta"): money(case.terminal_delta, base.currency),
                    T("chart_min_cash"): money(case.minimum_cash, base.currency),
                    T("reached_col"): T("not_applicable") if base.goal == 0
                    else (T("yes") if case.goal_reached else T("no")),
                } for case in comparisons]
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            st.caption(T("compare_horizon_disclaimer"))
    if custom_view.open:
        with custom_view:
            render_custom_comparison(base, int(horizon), T, money)
    if sensitivity_view.open:
        with sensitivity_view:
            with st.container():
                st.subheader(T("sens_title"))
                st.caption(T("sens_intro"))
                comparison_plan = replace(base, years=int(horizon))
                cache = st.session_state.get("_sensitivity_cache")
                if cache is not None and cache["plan"] != comparison_plan:
                    st.session_state.pop("_sensitivity_cache", None)
                    cache = None
                if st.button(
                    T("sens_run"), key="sensitivity_run", width="stretch",
                ):
                    with st.spinner(T("sens_calculating")):
                        report = analyze_assumptions(base, int(horizon))
                    st.session_state["_sensitivity_cache"] = {
                        "plan": comparison_plan, "report": report,
                    }
                    cache = st.session_state["_sensitivity_cache"]
                if cache is None:
                    st.info(T("sens_prompt"))
                else:
                    report = cache["report"]
                    if not report.impacts:
                        st.info(T("sens_no_inputs"))
                    else:
                        outcome = st.segmented_control(
                            T("sens_outcome"), [
                                "final_real_change", "final_nominal_change",
                                "minimum_cash_change",
                            ],
                            format_func=lambda key: T("sens_metric_" + key),
                            key="sensitivity_metric",
                            default="final_real_change", required=True,
                            width="stretch",
                        )
                        st.plotly_chart(
                            assumption_sensitivity_figure(
                                report, outcome, base.currency, T),
                            width="stretch", key="assumption_sensitivity_chart",
                            config={"displaylogo": False, "scrollZoom": False},
                        )
                        st.caption(T("sens_chart_help"))
                        st.caption(T("sens_scope", years=horizon))
                        if st.checkbox(
                            T("sens_details_toggle"), key="sensitivity_show_table",
                            value=False,
                        ):
                            rows = []
                            for item in report.impacts:
                                if item.kind == "amount":
                                    before = money(item.baseline_value, base.currency)
                                    after = money(item.tested_value, base.currency)
                                    variation = f"{item.change_size:+g}" + T("sens_pct")
                                else:
                                    before = f"{item.baseline_value:g}" + T("sens_pct")
                                    after = f"{item.tested_value:g}" + T("sens_pct")
                                    variation = f"{item.change_size:+g}" + T("sens_pp")
                                rows.append({
                                    T("sens_col_input"): T("sens_field_" + item.field),
                                    T("sens_col_change"): variation,
                                    T("sens_col_base"): before,
                                    T("sens_col_tested"): after,
                                    T("sens_metric_final_nominal_change"):
                                        money(item.final_nominal_change, base.currency),
                                    T("sens_metric_final_real_change"):
                                        money(item.final_real_change, base.currency),
                                    T("sens_metric_minimum_cash_change"):
                                        money(item.minimum_cash_change, base.currency),
                                })
                            st.dataframe(
                                pd.DataFrame(rows), hide_index=True, width="stretch",
                            )
                        st.caption(T("sens_limitations"))

    if stress_view.open:
        with stress_view:
            st.subheader(T("stress_title"))
            st.caption(T("stress_explanation"))
            stress_keys = st.multiselect(
                T("stress_choose"), PRESET_IDS,
                default=["job_gap", "unexpected_purchase"],
                format_func=lambda key: T("preset_" + key),
                key="stress_selection",
            )
            max_month = int(horizon) * 12
            if st.session_state.get("stress_start_month", 1) > max_month:
                st.session_state["stress_start_month"] = 1
            start_month = st.number_input(
                T("stress_start_month"), min_value=1, max_value=max_month,
                value=1, step=1, key="stress_start_month",
                help=T("stress_start_help"),
            )
            if stress_keys:
                selected_plan = replace(base, years=int(horizon))
                evaluations = evaluate_stresses(
                    selected_plan, tuple(stress_keys), int(start_month))
                if st.session_state.get("stress_focus_selected") not in (None, *stress_keys):
                    st.session_state.pop("stress_focus_selected", None)
                focus_key = st.selectbox(
                    T("stress_focus"), stress_keys,
                    format_func=lambda key: T("preset_" + key),
                    key="stress_focus_selected",
                )
                focused = next(e for e in evaluations if e.impact.key == focus_key)
                impacted_event = focused.impact.event
                start_year = selected_plan.start_year + (impacted_event.first_month - 1) // 12
                start_calendar_month = (impacted_event.first_month - 1) % 12 + 1
                st.caption(T("stress_event_window",
                             start=f"{start_year}-{start_calendar_month:02d}",
                             months=impacted_event.duration_months))
                a, b = st.columns(2, wrap=True)
                a.metric(T("stress_delta"),
                         money(focused.impact.terminal_delta, selected_plan.currency))
                b.metric(T("stress_peak_need"),
                         money(focused.peak_funding_need, selected_plan.currency),
                         help=T("stress_peak_need_help"))
                if focused.first_deficit_month is None:
                    st.info(T("stress_no_deficit"))
                else:
                    first = focused.first_deficit_month
                    first_year = selected_plan.start_year + (first - 1) // 12
                    first_calendar_month = (first - 1) % 12 + 1
                    st.warning(T(
                        "stress_deficit_detected",
                        date=f"{first_year}-{first_calendar_month:02d}",
                        count=focused.deficit_months))
                if focused.baseline_funding_need > 0:
                    st.info(T("stress_reference_already_negative",
                              amount=money(focused.baseline_funding_need,
                                           selected_plan.currency)))
                st.plotly_chart(
                    stress_liquidity_figure(
                        focused, selected_plan.start_year, selected_plan.currency, T),
                    width="stretch", key="stress_cash_trajectories",
                    config={"displaylogo": False, "scrollZoom": False},
                )
                st.caption(T("stress_chart_explanation"))
                with st.expander(T("stress_assumptions_title"), expanded=False):
                    st.caption(T("stress_assumptions_note"))
                    st.write(T("stress_assumption_upfront",
                               amount=money(impacted_event.upfront_cost,
                                            selected_plan.currency)))
                    st.write(T("stress_assumption_expense",
                               amount=money(impacted_event.monthly_expense,
                                            selected_plan.currency)))
                    st.write(T("stress_assumption_income",
                               amount=money(impacted_event.monthly_income_change,
                                            selected_plan.currency)))
                    st.caption(T("stress_extra_event_warning"))
                with st.expander(T("stress_details_title"), expanded=False):
                    stress_rows = []
                    for evaluation in evaluations:
                        first = evaluation.first_deficit_month
                        first_date = (f"{selected_plan.start_year + (first - 1) // 12}-"
                                      f"{(first - 1) % 12 + 1:02d}") if first else T("not_applicable")
                        stress_rows.append({
                            T("stress_scenario"): T("preset_" + evaluation.impact.key),
                            T("stress_delta"): money(evaluation.impact.terminal_delta,
                                                     selected_plan.currency),
                            T("stress_low_cash"): money(evaluation.impact.lowest_cash,
                                                       selected_plan.currency),
                            T("stress_peak_need"): money(evaluation.peak_funding_need,
                                                        selected_plan.currency),
                            T("stress_first_deficit"): first_date,
                            T("stress_deficit_months"): evaluation.deficit_months,
                            T("stress_new_deficit_months"): evaluation.newly_negative_months,
                        })
                    st.dataframe(pd.DataFrame(stress_rows), hide_index=True, width="stretch")
                st.caption(T("compare_stress_horizon", years=horizon))
                st.caption(T("stress_disclaimer"))
            else:
                st.info(T("stress_select_one"))
