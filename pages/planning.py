"""Responsive, fully localized financial planner with simple life-event cards."""
from __future__ import annotations

import csv
import hashlib
from dataclasses import replace
from io import StringIO
import json

import pandas as pd
import streamlit as st

from financial_adviser import __version__
from financial_adviser.engine import loan_payment, monte_carlo, project, solve_goal
from financial_adviser.charts import (
    DEFAULT_WEALTH_SERIES, WEALTH_SERIES, comparison_figure, event_markers,
    assumption_sensitivity_figure, custom_comparison_figure,
    household_figure, overlay_event_markers, resilience_figure,
    stress_liquidity_figure, uncertainty_figure, wealth_figure,
)
from financial_adviser.comparisons import build_comparisons, minimum_comparison_years
from financial_adviser.custom_comparison import (
    CUSTOM_AMOUNT_FIELDS, CUSTOM_RATE_FIELDS,
    CUSTOM_INTEGER_FIELDS, compare_custom_scenarios, make_custom_variant,
)
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.household_ui import render_household
from financial_adviser.models import LifeEvent, OneOff, Plan
from financial_adviser.insights import summarize_projection
from financial_adviser.resilience import analyze_liquidity
from financial_adviser.session_compat import normalize_plan
from financial_adviser.scenarios import PRESET_IDS, evaluate_stresses, proposed_event
from financial_adviser.sensitivity import analyze_assumptions
from financial_adviser.ui_i18n import category_label, canonical_category, t

LANG = st.session_state.get("language_choice", "fr")
T = lambda key, **args: t(LANG, key, **args)
CATEGORIES = ("child", "health", "purchase", "unemployment", "education", "relocation", "other")


def demo(country: str) -> Plan:
    if country == "VN":
        return Plan(country="VN", currency="VND", initial_cash=150_000_000,
                    initial_investments=250_000_000, monthly_income=50_000_000,
                    monthly_expenses=30_000_000, monthly_investment=10_000_000,
                    goal=2_000_000_000)
    return Plan()


def money(amount: float, currency: str) -> str:
    digits = 0 if currency == "VND" else 2
    return f"{amount:,.{digits}f}".replace(",", " ") + (" ₫" if currency == "VND" else " €")


def parse_oneoffs(raw: str, years: int) -> tuple[OneOff, ...]:
    if not raw.strip():
        return ()
    lines = list(csv.reader(StringIO(raw), skipinitialspace=True))
    if len(lines) > 100:
        raise ValueError("too many events")
    parsed = []
    for row in lines:
        if not row or not any(s.strip() for s in row):
            continue
        if len(row) not in (2, 3):
            raise ValueError("invalid event row")
        parsed.append(OneOff(int(row[0].strip()), float(row[1].strip()),
                             row[2].strip() if len(row) == 3 else ""))
    if any(not 1 <= item.month <= years * 12 for item in parsed):
        raise ValueError("invalid event month")
    return tuple(parsed)


def remember_custom_mode() -> None:
    """Retain custom-edit vs JSON-import mode across lazy tab switches."""
    st.session_state["_last_custom_input_mode"] = st.session_state["custom_input_mode"]


def remember_analysis_view() -> None:
    """Preserve the selected analysis when lazy tabs are unmounted."""
    label = st.session_state.get("comparison_analysis_navigation")
    for name in ("variants", "custom", "sensitivity", "stress"):
        if label == T("analysis_" + name):
            st.session_state["_last_analysis_view"] = name
            break


def reset_inputs() -> None:
    """Clear widgets and rehydrate them before a new plan is rendered."""
    for key in list(st.session_state):
        if key.startswith(("field_", "evt_", "mc_", "preset_", "stress_", "child_", "adult_", "household_", "dependent_")):
            del st.session_state[key]
    st.session_state.pop("event_drafts", None)
    st.session_state.pop("event_expanded_id", None)
    st.session_state.pop("household_children", None)
    st.session_state.pop("household_adults", None)
    st.session_state.pop("household_dependents", None)
    st.session_state.pop("household_dependent_id", None)
    st.session_state.pop("household_child_id", None)
    st.session_state.pop("household_adult_id", None)
    st.session_state.pop("goal_alternatives", None)
    st.session_state.pop("goal_query", None)
    st.session_state.pop("goal_target_input", None)
    st.session_state.pop("goal_horizon_input", None)
    for key in (
        "comparison_horizon", "_comparison_source", "chart_show_events",
        "_sensitivity_cache", "sensitivity_metric", "sensitivity_show_table",
        "_last_analysis_view", "_last_custom_input_mode",
        "_custom_comparison", "_custom_form_source", "custom_input_mode",
        "custom_metric", "custom_import",
    ):
        st.session_state.pop(key, None)
    for field in (*CUSTOM_AMOUNT_FIELDS, *CUSTOM_RATE_FIELDS,
                  *CUSTOM_INTEGER_FIELDS):
        st.session_state.pop("custom_field_" + field, None)
    # Clearing a widget after it has been instantiated may leave its old
    # browser-side value until the next client update. Rehydrate on the next
    # script run, before any input widget has been declared.
    st.session_state["_restore_plan_widgets"] = bool(st.session_state.get("confirmed_inputs"))


def hydrate_inputs(plan: Plan) -> None:
    """Restore the complete saved plan into Streamlit widgets before rendering."""
    values = {
        "field_income": float(plan.monthly_income),
        "field_expenses": float(plan.monthly_expenses),
        "field_goal": float(plan.goal),
        "field_contribution": float(plan.monthly_investment),
        "field_cash": float(plan.initial_cash),
        "field_investments": float(plan.initial_investments),
        "field_years": int(plan.years),
        "field_start_year": int(plan.start_year),
        "field_income_growth": float(plan.income_growth_pct),
        "field_expense_growth": float(plan.expense_growth_pct),
        "field_cash_return": float(plan.cash_return_pct),
        "field_investment_return": float(plan.investment_return_pct),
        "field_inflation": float(plan.inflation_pct),
        "field_volatility": float(plan.investment_volatility_pct),
        "field_loan": float(plan.loan_balance),
        "field_loan_rate": float(plan.loan_apr_pct),
        "field_loan_years": int(plan.loan_years),
        "field_oneoffs": "\n".join(
            f"{item.month},{item.amount},{item.description}" for item in plan.one_offs),
    }
    for key, value in values.items():
        st.session_state[key] = value


def init_events(plan: Plan) -> None:
    if "event_drafts" not in st.session_state:
        st.session_state.event_drafts = [
            {"id": i + 1, "category": canonical_category(e.category), "label": e.label,
             "first_month": e.first_month, "duration_months": e.duration_months,
             "monthly_expense": e.monthly_expense, "monthly_income_change": e.monthly_income_change,
             "upfront_cost": e.upfront_cost}
            for i, e in enumerate(plan.life_events)
        ]
        st.session_state.event_next_id = len(st.session_state.event_drafts) + 1


def draw_events(start_year: int, years: int, currency: str, income: float, expenses: float) -> tuple[LifeEvent, ...]:
    """Editable stacked cards, stable widget keys even after deleting a card."""
    init_events(st.session_state.plan)
    with st.container(border=True):
        st.subheader("👨‍👩‍👧‍👦 " + T("life_title"))
        st.caption(T("life_help"))
        if st.button("＋ " + T("life_add"), key="add_life_event", width="stretch"):
            if len(st.session_state.event_drafts) >= 100:
                st.warning(T("max_events"))
            else:
                eid = st.session_state.event_next_id
                st.session_state.event_next_id += 1
                st.session_state.event_drafts.append({"id": eid, "category": "other", "label": "",
                    "first_month": 1, "duration_months": 1, "monthly_expense": 0.0,
                    "monthly_income_change": 0.0, "upfront_cost": 0.0})
                st.rerun()
        st.subheader(T("preset_title"))
        st.caption(T("preset_hint"))
        selected_template = st.selectbox(T("preset_choose"),
            ("none",) + PRESET_IDS, key="preset_selected",
            format_func=lambda value: T("preset_none") if value == "none" else T("preset_" + value))
        if selected_template != "none":
            a, b = st.columns(2, wrap=True)
            with a:
                chosen_year = st.number_input(T("life_year"), min_value=start_year,
                    max_value=start_year + years - 1, value=start_year, key="preset_year")
            with b:
                chosen_month = st.selectbox(T("life_month"), list(range(1, 13)), key="preset_month")
            proposed_month = (int(chosen_year) - start_year) * 12 + int(chosen_month)
            preview_plan = replace(st.session_state.plan, years=years, life_events=(),
                one_offs=(), monthly_income=max(0.0, income), monthly_expenses=max(0.0, expenses))
            suggestion = proposed_event(preview_plan, selected_template, proposed_month,
                label=T("preset_" + selected_template))
            net_cost = suggestion.upfront_cost + suggestion.duration_months * (
                suggestion.monthly_expense - suggestion.monthly_income_change)
            st.caption(T("preset_preview", duration=suggestion.duration_months,
                cost=money(net_cost, currency)))
            st.caption(T("preset_double_count"))
            if st.button("＋ " + T("preset_add"), key="preset_confirm_add", width="stretch"):
                if len(st.session_state.event_drafts) >= 100:
                    st.warning(T("max_events"))
                else:
                    eid = st.session_state.event_next_id
                    st.session_state.event_next_id += 1
                    st.session_state.event_drafts.append({
                    "id": eid, "category": suggestion.category, "label": suggestion.label,
                    "first_month": suggestion.first_month, "duration_months": suggestion.duration_months,
                    "monthly_expense": suggestion.monthly_expense,
                    "monthly_income_change": suggestion.monthly_income_change,
                    "upfront_cost": suggestion.upfront_cost})
                    st.rerun()
        if not st.session_state.event_drafts:
            st.caption(T("life_empty"))
        for index, draft in enumerate(st.session_state.event_drafts, start=1):
            eid = draft["id"]
            prefix = f"evt_{eid}_"
            initial_month = max(1, int(draft["first_month"]))
            initial_year = start_year + (initial_month - 1) // 12
            initial_year = max(start_year, min(start_year + years - 1, initial_year))
            initial_cal_month = (initial_month - 1) % 12 + 1
            event_title = draft["label"].strip() or T("life_event", index=index)
            event_date = f"{initial_year}-{initial_cal_month:02d}"
            event_months = int(draft["duration_months"])
            open_key = prefix + "open"
            with st.container(border=True):
                is_open = st.session_state.get(open_key, False)
                head, delete = st.columns([8, 2], vertical_alignment="center", gap="small", wrap=False)
                if head.button(
                    f"{'▾' if is_open else '▸'} 📅 {event_title} · {event_date} · {event_months} {T('months')}",
                    key=prefix + "toggle", type="tertiary", width="stretch"):
                    st.session_state[open_key] = not is_open
                    st.rerun()
                if delete.button("✕", key=prefix + "remove",
                                 help=T("remove_card_help"), width="stretch"):
                    st.session_state.event_drafts = [
                        x for x in st.session_state.event_drafts if x["id"] != eid]
                    for old_key in list(st.session_state):
                        if old_key.startswith(prefix):
                            del st.session_state[old_key]
                    st.rerun()
                if is_open:
                    a, b = st.columns(2, wrap=True)
                    with a:
                        category = st.selectbox(T("life_type"), CATEGORIES,
                            index=CATEGORIES.index(draft["category"]), key=prefix + "category",
                            format_func=lambda value: category_label(LANG, value))
                    with b:
                        label = st.text_input(T("life_label"), value=draft["label"],
                                              key=prefix + "label", placeholder=T("life_label_hint"))
                    y, m, d = st.columns(3, wrap=True)
                    with y:
                        first_year = st.number_input(T("life_year"), min_value=start_year,
                            max_value=start_year + years - 1, value=initial_year, step=1, key=prefix + "year")
                    with m:
                        cal_month = st.selectbox(T("life_month"), list(range(1, 13)),
                            index=initial_cal_month - 1, key=prefix + "month")
                    first_month = (int(first_year) - start_year) * 12 + int(cal_month)
                    with d:
                        duration = st.number_input(T("life_duration"), min_value=1, max_value=720,
                            value=max(1, int(draft["duration_months"])), step=1, key=prefix + "duration")
                    a, b = st.columns(2, wrap=True)
                    amount_step = 100_000.0 if currency == "VND" else 100.0
                    with a:
                        extra = st.number_input(T("life_extra"), min_value=0.0,
                            value=float(draft["monthly_expense"]), step=amount_step,
                            help=T("life_extra_help"), key=prefix + "expense")
                    with b:
                        income_change = st.number_input(T("life_income_change"),
                            value=float(draft["monthly_income_change"]), step=amount_step,
                            help=T("life_income_change_help"), key=prefix + "income")
                    upfront = st.number_input(T("life_upfront"), min_value=0.0,
                        value=float(draft["upfront_cost"]), step=amount_step,
                        help=T("life_upfront_help"), key=prefix + "upfront")
                    draft.update(category=category, label=label, first_month=first_month,
                                 duration_months=int(duration), monthly_expense=extra,
                                 monthly_income_change=income_change, upfront_cost=upfront)
                    net_cost = upfront + int(duration) * (extra - income_change)
                    st.caption(T("life_total", value=money(net_cost, currency)))
        st.caption(T("life_summary"))
    return tuple(LifeEvent(category=e["category"], label=e["label"].strip(),
                    first_month=e["first_month"], duration_months=e["duration_months"],
                    monthly_expense=e["monthly_expense"], monthly_income_change=e["monthly_income_change"],
                    upfront_cost=e["upfront_cost"]) for e in st.session_state.event_drafts)



def reset_wealth_curves() -> None:
    """Return to the simple two-curve default on explicit request."""
    for field in WEALTH_SERIES:
        st.session_state["chart_curve_" + field] = field in DEFAULT_WEALTH_SERIES


@st.fragment
def render_result_charts(q: Plan, df: pd.DataFrame, mc: object | None) -> None:
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





def render_financial_overview(plan: Plan, df: pd.DataFrame) -> None:
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
def render_resilience_panel(plan: Plan, df: pd.DataFrame) -> None:
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




def render_custom_comparison(base: Plan, years: int) -> None:
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


@st.fragment
def render_comparison_tab(base: Plan) -> None:
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
        on_change=remember_analysis_view,
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
            render_custom_comparison(base, int(horizon))
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


if "plan" not in st.session_state:
    st.session_state.plan = demo("FR")
else:
    # A browser tab can survive a code deployment with a pre-household Plan.
    # Preserve all compatible saved values instead of failing on missing
    # children/adults fields. Never silently replace an unconvertible plan.
    try:
        updated_plan, migrated = normalize_plan(st.session_state.plan)
    except (ValueError, TypeError, AttributeError):
        st.error(T("session_migration_error"))
        st.stop()
    if migrated:
        st.session_state.plan = updated_plan
        st.session_state.result = None
        reset_inputs()
        st.session_state.session_migration_notice = True
if "result" not in st.session_state:
    st.session_state.result = None
if "confirmed_inputs" not in st.session_state:
    st.session_state.confirmed_inputs = False
if st.session_state.pop("_restore_plan_widgets", False):
    hydrate_inputs(st.session_state.plan)

with st.sidebar:
    st.caption(f"v{__version__}")
    if "country_choice" not in st.session_state:
        st.session_state.country_choice = st.session_state.plan.country
    if "pending_country" in st.session_state:
        st.session_state.country_choice = st.session_state.pop("pending_country")
    country = st.session_state.plan.country
    st.divider()

header_col, country_col = st.columns([2.1, 1], gap="large", vertical_alignment="center")
with country_col:
    country = st.selectbox(T("country"), ["FR", "VN"], key="country_choice",
        format_func=lambda code: "France (EUR)" if code == "FR" else "Việt Nam (VND)")
if country != st.session_state.plan.country:
    st.warning(T("country_confirm_text"))
    a, b = st.columns(2, wrap=True)
    if a.button(T("confirm_replace"), key="confirm_country", width="stretch"):
        st.session_state.plan = demo(country)
        st.session_state.confirmed_inputs = False
        st.session_state.result = None
        st.session_state.example_pending = False
        reset_inputs()
        st.rerun()
    if b.button(T("cancel_replace"), key="cancel_country", width="stretch"):
        st.session_state.country_choice = st.session_state.plan.country
        st.rerun()
p = st.session_state.plan
with header_col:
    st.title("Financial Adviser")
    st.caption(T("caption") + f" · v{__version__}")
if st.session_state.pop("session_migration_notice", False):
    st.info(T("session_migration_ok"))
if st.button("📋 " + T("example"), key="load_demo", width="stretch"):
    st.session_state.example_pending = True
if st.session_state.get("example_pending"):
    st.warning(T("example_confirm_text"))
    a, b = st.columns(2, wrap=True)
    if a.button(T("confirm_replace"), key="confirm_example", width="stretch"):
        st.session_state.example_pending = False
        st.session_state.plan = demo(st.session_state.plan.country)
        st.session_state.confirmed_inputs = True
        st.session_state.result = None
        reset_inputs()
        st.rerun()
    if b.button(T("cancel_replace"), key="cancel_example", width="stretch"):
        st.session_state.example_pending = False
        st.rerun()

with st.expander("🗂️ " + T("scenario_files"), expanded=False):
    uploaded = st.file_uploader(T("import"), type=["json"], max_upload_size=1)
    if uploaded is not None and st.button(T("load"), width="stretch"):
        try:
            imported = load_plan(uploaded.getvalue())
            st.session_state.plan = imported
            st.session_state.pending_country = imported.country
            st.session_state.confirmed_inputs = True
            st.session_state.result = None
            reset_inputs()
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError):
            st.error(T("invalid_import"))
    st.download_button(T("export_saved"), data=dump_plan(st.session_state.plan),
                       file_name="financial_adviser_scenario.json", mime="application/json",
                       disabled=not st.session_state.confirmed_inputs, width="stretch")

with st.expander("ℹ️ " + T("disclaimer_title"), expanded=False):
    st.info(T("disclaimer"))

# The first visit is a clean, full-width input experience. After the user
# explicitly calculates, desktop shows inputs and results side-by-side.
# Responsive Streamlit columns stack vertically on narrow viewports.
if st.session_state.result is None:
    plan_tab = st.container()
else:
    editor_col, dashboard_col = st.columns(
        [1.0, 1.6], gap="large", vertical_alignment="top")
    with editor_col:
        plan_tab = st.container()
    with dashboard_col:
        results_tab, goal_tab, compare_tab = st.tabs(
            [T("tab_results"), T("tab_goal"), T("tab_compare")],
            key="main_results_navigation", on_change="rerun",
        )

with plan_tab:
    st.subheader(T("basic"))
    st.caption(T("plan_intro"))
    with st.popover("📊 " + T("nav_benchmarks")):
        st.caption(T("reference_hint"))
        if st.button(T("nav_benchmarks"), key="open_statistical_references"):
            st.switch_page("pages/benchmarks.py")
    if not st.session_state.confirmed_inputs:
        st.warning(T("required_warning"))
    a, b = st.columns(2, wrap=True)
    step = 100_000.0 if p.currency == "VND" else 100.0
    with a:
        income = st.number_input(T("income") + " (" + T("required") + ")", min_value=0.0,
            value=float(p.monthly_income) if st.session_state.confirmed_inputs else None,
            step=step, key="field_income", placeholder=T("required"))
        expenses = st.number_input(T("expenses") + " (" + T("required") + ")", min_value=0.0,
            value=float(p.monthly_expenses) if st.session_state.confirmed_inputs else None,
            step=step, key="field_expenses", placeholder=T("required"))
        goal = st.number_input(T("goal") + " (" + T("required") + ")", min_value=0.0,
            value=float(p.goal) if st.session_state.confirmed_inputs else None,
            step=step * 10, key="field_goal", placeholder=T("required"))
        contribution = st.number_input(T("contribution"), min_value=0.0,
            value=float(p.monthly_investment) if st.session_state.confirmed_inputs else 0.0,
            step=step, key="field_contribution")
    with b:
        cash = st.number_input(T("cash"), min_value=0.0,
            value=float(p.initial_cash) if st.session_state.confirmed_inputs else 0.0,
            step=step * 10, key="field_cash")
        investments = st.number_input(T("investments"), min_value=0.0,
            value=float(p.initial_investments) if st.session_state.confirmed_inputs else 0.0,
            step=step * 10, key="field_investments")
        years = st.number_input(T("horizon"), min_value=1, max_value=60, value=p.years, step=1, key="field_years")
        start_year = st.number_input(T("start_year"), min_value=2020, max_value=2100,
                                     value=p.start_year, step=1, key="field_start_year")
 
    # Keep optional assumptions available without pushing household editing off-screen.
    # Streamlit still instantiates widgets inside a collapsed expander.
    with st.expander("⚙️ " + T("advanced"), expanded=False):
        with st.container(border=True):
            a, b = st.columns(2, wrap=True)
            with a:
                income_growth = st.number_input(T("growth_income"), min_value=-90., max_value=200., value=float(p.income_growth_pct), step=0.5, key="field_income_growth")
                spending_growth = st.number_input(T("growth_expenses"), min_value=-90., max_value=200., value=float(p.expense_growth_pct), step=0.5, key="field_expense_growth")
                cash_return = st.number_input(T("cash_return"), min_value=-90., max_value=200., value=float(p.cash_return_pct), step=0.5, key="field_cash_return")
            with b:
                investment_return = st.number_input(T("investment_return"), min_value=-90., max_value=200., value=float(p.investment_return_pct), step=0.5, key="field_investment_return")
                inflation = st.number_input(T("inflation"), min_value=-90., max_value=200., value=float(p.inflation_pct), step=0.5, key="field_inflation")
                volatility = st.number_input(T("volatility"), min_value=0., max_value=100., value=float(p.investment_volatility_pct), step=1., key="field_volatility")
        with st.container(border=True):
            st.subheader("🏡 " + T("loan_title"))
            a, b, c = st.columns(3, wrap=True)
            with a:
                loan = st.number_input(T("loan_balance"), min_value=0., value=float(p.loan_balance), step=step * 10, key="field_loan")
            with b:
                loan_rate = st.number_input(T("loan_apr"), min_value=0., max_value=100., value=float(p.loan_apr_pct), step=0.25, key="field_loan_rate")
            with c:
                loan_years = st.number_input(T("loan_years"), min_value=1, max_value=60, value=p.loan_years, key="field_loan_years")
            st.caption(T("loan_hint"))
        with st.container(border=True):
            st.subheader("📅 " + T("extra_title"))
            previous = "\n".join(f"{e.month},{e.amount},{e.description}" for e in p.one_offs)
            oneoffs_text = st.text_area(T("extra_label"), value=previous,
                help=T("extra_hint"), key="field_oneoffs")
        enable_mc = st.checkbox(T("simulate_mc"), value=False, key="mc_enable")
        a, b = st.columns(2, wrap=True)
        with a:
            n_paths = st.selectbox(T("paths"), options=[250, 500, 1000, 2000, 5000],
                index=2, key="mc_paths", disabled=not enable_mc)
        with b:
            seed = st.number_input(T("seed"), min_value=0, max_value=2**31 - 1,
                value=42, key="mc_seed", disabled=not enable_mc)

# Keep family and life-event editors in the scenario panel after a projection.
# Before the first run they share the full width; beside the results dashboard
# they stack vertically so that narrow columns remain usable on desktop/mobile.
with plan_tab:
    if st.session_state.result is None:
        household_col, event_col = st.columns([1, 1], gap="large", vertical_alignment="top")
    else:
        household_col, event_col = st.container(), st.container()
    with household_col:
        children, adults, dependents = render_household(
            p, int(years), int(start_year), float(expenses or 0.0), LANG, step)
    with event_col:
        events = draw_events(int(start_year), int(years), p.currency,
                             float(income or 0.0), float(expenses or 0.0))
with plan_tab:
    if income is not None and expenses is not None:
        operating_surplus = (float(income) - float(expenses) -
            loan_payment(float(loan), float(loan_rate), int(loan_years)))
        st.metric(T("free_cash"), money(operating_surplus, p.currency))
        if float(contribution) > max(0.0, operating_surplus):
            st.warning(T("contribution_over_surplus"))
    # Explicitly warn that result tables and inverse scenarios still use last saved inputs.
    dirty = st.session_state.result is not None and (
        income != p.monthly_income or expenses != p.monthly_expenses
        or goal != p.goal or contribution != p.monthly_investment
        or cash != p.initial_cash or investments != p.initial_investments
        or years != p.years or start_year != p.start_year
        or tuple(events) != p.life_events
        or children != p.children or adults != p.adults
        or dependents != p.dependents
        or income_growth != p.income_growth_pct or spending_growth != p.expense_growth_pct
        or cash_return != p.cash_return_pct or investment_return != p.investment_return_pct
        or inflation != p.inflation_pct or volatility != p.investment_volatility_pct
        or loan != p.loan_balance or loan_rate != p.loan_apr_pct
        or loan_years != p.loan_years
        or oneoffs_text.strip() != "\n".join(
            f"{e.month},{e.amount},{e.description}" for e in p.one_offs).strip()
    )
    if dirty:
        st.warning(T("edited_not_run"))
    if st.button("▶ " + T("run"), type="primary", width="stretch", key="run_projection"):
        try:
            if income is None or expenses is None or goal is None:
                st.error(T("required_error"))
            elif any(not e.label or not 1 <= e.first_month or
                     e.first_month + e.duration_months - 1 > years * 12 for e in events):
                st.error(T("event_error"))
            else:
                new_plan = Plan(country=p.country, currency=p.currency, start_year=int(start_year), years=int(years),
                    initial_cash=float(cash), initial_investments=float(investments),
                    monthly_income=float(income), monthly_expenses=float(expenses), monthly_investment=float(contribution),
                    income_growth_pct=income_growth, expense_growth_pct=spending_growth,
                    cash_return_pct=cash_return, investment_return_pct=investment_return,
                    investment_volatility_pct=volatility, inflation_pct=inflation,
                    loan_balance=loan, loan_apr_pct=loan_rate, loan_years=int(loan_years),
                    goal=float(goal), one_offs=parse_oneoffs(oneoffs_text, years),
                    life_events=events, children=children, adults=adults,
                    dependents=dependents)
                new_plan.validate()
                with st.spinner(T("running")):
                    result = project(new_plan)
                    mc = monte_carlo(new_plan, n_paths=int(n_paths), seed=int(seed)) if enable_mc else None
                is_first_projection = st.session_state.result is None
                st.session_state.plan = new_plan
                st.session_state.confirmed_inputs = True
                st.session_state.result = {"df": result, "mc": mc, "plan": new_plan}
                st.session_state.pop("goal_alternatives", None)
                dirty = False
                if is_first_projection:
                    # Create the dashboard columns on the next script run.
                    st.session_state["first_projection_notice"] = True
                    st.rerun()
                st.success(T("done"))
                # The Run button is at the end of a long editable scenario.
                # Show the outcome here as well so the user needn't scroll
                # back to the dashboard header to learn whether it worked.
                st.metric(T("net_worth"), money(float(result.net_worth.iloc[-1]), new_plan.currency))
                if (result.cash < 0).any():
                    st.warning(T("negative_cash"))
        except (ValueError, OverflowError, ZeroDivisionError, TypeError):
            st.error(T("invalid"))

if st.session_state.result is not None:
    if results_tab.open:
        with results_tab:
            st.divider()
            st.subheader(T("tab_results"))
            if st.session_state.pop("first_projection_notice", False):
                st.success(T("done"))
            if dirty:
                st.warning(T("outdated_result"))
            result = st.session_state.result
            if result is None:
                st.info(T("no_result"))
            else:
                q, df = result["plan"], result["df"]
                last = df.iloc[-1]
                a, b = st.columns(2, wrap=True)
                c, d = st.columns(2, wrap=True)
                a.metric(T("net_worth"), money(float(last.net_worth), q.currency))
                b.metric(T("net_worth_real"), money(float(last.net_worth_real), q.currency))
                c.metric(T("remaining_loan"), money(float(last.loan_balance), q.currency))
                d.metric(T("goal_reached"), T("not_applicable") if q.goal == 0
                         else (T("yes") if last.net_worth >= q.goal else T("no")))
                initial_loan_payment = loan_payment(q.loan_balance, q.loan_apr_pct, q.loan_years)
                liquidity = analyze_liquidity(q, df)
                runway = liquidity.static_reserve_months
                a2, b2 = st.columns(2, wrap=True)
                a2.metric(T("cash_buffer"), (f"{runway:.1f} " + T("months"))
                          if runway is not None else T("not_applicable"),
                          help=T("cash_buffer_help"))
                b2.metric(T("debt_service"), (f"{100 * initial_loan_payment / q.monthly_income:.1f}%")
                          if q.monthly_income > 0 else T("not_applicable"),
                          help=T("debt_service_help"))
                render_financial_overview(q, df)
                # Stock, monthly-flow and uncertainty plots share one chart area.
                # Controls are isolated so selecting a curve does not rerun the engine.
                render_result_charts(q, df, result["mc"])
                render_resilience_panel(q, df)
                with st.expander(T("yearly"), expanded=False):
                    yearly = df.iloc[::12][["year", "cash", "investments", "loan_balance", "net_worth", "net_worth_real"]]
                    st.dataframe(yearly.rename(columns={"year": T("year"), "cash": T("cash_name"),
                        "investments": T("investments_name"), "loan_balance": T("loan_name"),
                        "net_worth": T("net_worth"), "net_worth_real": T("net_worth_real")}).round(2),
                        hide_index=True, width="stretch")
                st.download_button(T("export_csv"), df.to_csv(index=False).encode("utf-8"),
                                   "financial_projection_monthly.csv", mime="text/csv")
                st.caption(T("result_limit"))

    if goal_tab.open:
        with goal_tab:
            st.divider()
            if dirty:
                st.warning(T("outdated_result"))
                st.info(T("needs_run"))
            elif not st.session_state.confirmed_inputs:
                pass  # Don't repeat the empty-results notice below the main dashboard.
            else:
                st.subheader(T("tab_goal"))
                st.caption(T("goal_intro"))
                reference = st.session_state.plan
                a, b = st.columns(2, wrap=True)
                with a:
                    target = st.number_input(T("goal_target"), min_value=0.0, value=float(reference.goal),
                                              step=1000.0, key="goal_target_input")
                with b:
                    last_event = max([0] + [e.first_month + e.duration_months - 1 for e in reference.life_events]
                                     + [e.month for e in reference.one_offs]
                                     + [c.arrival_month for c in reference.children])
                    min_years = max(1, (last_event + 11) // 12)
                    horizon = st.number_input(T("goal_years"), min_value=min_years, max_value=60, value=max(min_years, reference.years), step=1,
                                        key="goal_horizon_input")
                if st.button(T("goal_calculate"), type="primary", width="stretch"):
                    try:
                        st.session_state.goal_alternatives = solve_goal(reference, float(target), int(horizon))
                        st.session_state.goal_query = (reference, float(target), int(horizon))
                    except (ValueError, OverflowError):
                        st.error(T("invalid"))
                if "goal_alternatives" in st.session_state:
                    stale = st.session_state.get("goal_query") != (reference, float(target), int(horizon))
                    if stale:
                        st.warning(T("goal_stale"))
                    for idx, solution in enumerate(st.session_state.goal_alternatives):
                        with st.container(border=True):
                            st.markdown("**" + T("goal_" + solution.lever) + "**")
                            if not solution.feasible:
                                st.warning(T("goal_unfeasible"))
                            else:
                                st.metric(T("goal_required"), money(solution.amount, reference.currency))
                                projection = project(solution.scenario)
                                st.caption(f"{T('goal_result')}: {money(float(projection.net_worth.iloc[-1]), reference.currency)}"
                                           f" · {T('goal_min_cash')}: {money(float(projection.cash.min()), reference.currency)}")
                                if st.button(T("goal_apply"), key=f"solution_{idx}", disabled=stale, width="stretch"):
                                    st.session_state.plan = solution.scenario
                                    st.session_state.confirmed_inputs = True
                                    st.session_state.result = {"df": projection, "mc": None, "plan": solution.scenario}
                                    reset_inputs()
                                    st.rerun()
                    st.caption(T("goal_disclaimer"))

    if compare_tab.open:
        with compare_tab:
            st.divider()
            if dirty:
                st.warning(T("outdated_result"))
                st.info(T("needs_run"))
            elif st.session_state.confirmed_inputs:
                render_comparison_tab(st.session_state.plan)
