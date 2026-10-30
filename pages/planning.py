"""Responsive, fully localized financial planner with simple life-event cards."""
from __future__ import annotations

import csv
from dataclasses import replace
from io import StringIO
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_adviser import __version__
from financial_adviser.engine import loan_payment, monte_carlo, project, solve_goal
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import LifeEvent, OneOff, Plan
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


def reset_inputs() -> None:
    """Discard old widget values after loading another plan/country/goal solution."""
    for key in list(st.session_state):
        if key.startswith("field_") or key.startswith("evt_") or key.startswith("mc_"):
            del st.session_state[key]
    st.session_state.pop("event_drafts", None)
    st.session_state.pop("goal_alternatives", None)
    st.session_state.pop("goal_query", None)
    st.session_state.pop("goal_target_input", None)
    st.session_state.pop("goal_horizon_input", None)


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


def draw_events(start_year: int, years: int, currency: str) -> tuple[LifeEvent, ...]:
    """Editable stacked cards, stable widget keys even after deleting a card."""
    init_events(st.session_state.plan)
    with st.expander("👨‍👩‍👧‍👦 " + T("life_title"), expanded=bool(st.session_state.event_drafts)):
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
        if not st.session_state.event_drafts:
            st.caption(T("life_empty"))
        for index, draft in enumerate(st.session_state.event_drafts, start=1):
            eid = draft["id"]
            prefix = f"evt_{eid}_"
            initial_month = max(1, int(draft["first_month"]))
            initial_year = start_year + (initial_month - 1) // 12
            initial_year = max(start_year, min(start_year + years - 1, initial_year))
            initial_cal_month = (initial_month - 1) % 12 + 1
            with st.container(border=True):
                a, b = st.columns([3, 1], wrap=True)
                a.markdown("**" + T("life_event", index=index) + "**")
                if b.button("✕ " + T("life_remove"), key=prefix + "remove", width="stretch"):
                    st.session_state.event_drafts = [x for x in st.session_state.event_drafts if x["id"] != eid]
                    for key in list(st.session_state):
                        if key.startswith(prefix):
                            del st.session_state[key]
                    st.rerun()
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
                a, b, c = st.columns(3, wrap=True)
                amount_step = 100_000.0 if currency == "VND" else 100.0
                with a:
                    extra = st.number_input(T("life_extra"), min_value=0.0,
                        value=float(draft["monthly_expense"]), step=amount_step, key=prefix + "expense")
                with b:
                    income_change = st.number_input(T("life_income_change"),
                        value=float(draft["monthly_income_change"]), step=amount_step, key=prefix + "income")
                with c:
                    upfront = st.number_input(T("life_upfront"), min_value=0.0,
                        value=float(draft["upfront_cost"]), step=amount_step, key=prefix + "upfront")
                draft.update(category=category, label=label, first_month=first_month,
                             duration_months=int(duration), monthly_expense=extra,
                             monthly_income_change=income_change, upfront_cost=upfront)
        st.caption(T("life_summary"))
    return tuple(LifeEvent(category=e["category"], label=e["label"].strip(),
                    first_month=e["first_month"], duration_months=e["duration_months"],
                    monthly_expense=e["monthly_expense"], monthly_income_change=e["monthly_income_change"],
                    upfront_cost=e["upfront_cost"]) for e in st.session_state.event_drafts)


if "plan" not in st.session_state:
    st.session_state.plan = demo("FR")
if "result" not in st.session_state:
    st.session_state.result = None
if "confirmed_inputs" not in st.session_state:
    st.session_state.confirmed_inputs = False

with st.sidebar:
    st.caption(f"v{__version__}")
    if "country_choice" not in st.session_state:
        st.session_state.country_choice = st.session_state.plan.country
    if "pending_country" in st.session_state:
        st.session_state.country_choice = st.session_state.pop("pending_country")
    country = st.selectbox(T("country"), ["FR", "VN"], key="country_choice",
        format_func=lambda code: "France (EUR)" if code == "FR" else "Việt Nam (VND)")
    if country != st.session_state.plan.country:
        st.session_state.plan = demo(country)
        st.session_state.confirmed_inputs = False
        st.session_state.result = None
        reset_inputs()
        st.info(T("country_note"))
        st.rerun()
    advanced = st.toggle(T("mode_advanced"), key="advanced_choice", value=False)
    st.divider()
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
    if st.button("📋 " + T("example"), width="stretch"):
        st.session_state.plan = demo(country)
        st.session_state.confirmed_inputs = True
        st.session_state.result = None
        reset_inputs()
        st.rerun()
    st.download_button(T("export"), data=dump_plan(st.session_state.plan),
                       file_name="financial_adviser_scenario.json", mime="application/json", width="stretch")

p = st.session_state.plan
st.title("Financial Adviser")
st.caption(T("caption"))
with st.expander("ℹ️ " + T("disclaimer_title"), expanded=False):
    st.info(T("disclaimer"))

plan_tab, results_tab, goal_tab, compare_tab = st.tabs([
    "⚙️ " + T("tab_plan"), "📊 " + T("tab_results"),
    "🎯 " + T("tab_goal"), "🧭 " + T("tab_compare")])

with plan_tab:
    st.subheader(T("basic"))
    st.caption(T("plan_intro"))
    if st.button("📊 " + T("nav_benchmarks"), key="show_statistical_references", width="stretch"):
        st.switch_page("pages/benchmarks.py")
    if not st.session_state.confirmed_inputs:
        st.warning(T("required_warning"))
    a, b = st.columns(2, wrap=True)
    step = 100_000.0 if p.currency == "VND" else 100.0
    with a:
        income = st.number_input(T("income") + " *", min_value=0.0,
            value=float(p.monthly_income) if st.session_state.confirmed_inputs else None,
            step=step, key="field_income", placeholder=T("required"))
        expenses = st.number_input(T("expenses") + " *", min_value=0.0,
            value=float(p.monthly_expenses) if st.session_state.confirmed_inputs else None,
            step=step, key="field_expenses", placeholder=T("required"))
        goal = st.number_input(T("goal") + " *", min_value=0.0,
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
        years = st.slider(T("horizon"), 1, 60, value=p.years, key="field_years")
        start_year = st.number_input(T("start_year"), min_value=2020, max_value=2100,
                                     value=p.start_year, step=1, key="field_start_year")
    if income is not None and expenses is not None:
        st.metric(T("free_cash"), money(income - expenses - loan_payment(p.loan_balance, p.loan_apr_pct, p.loan_years), p.currency))

    events = draw_events(int(start_year), int(years), p.currency)

    if advanced:
        with st.expander("📐 " + T("advanced"), expanded=False):
            a, b = st.columns(2, wrap=True)
            with a:
                income_growth = st.number_input(T("growth_income"), min_value=-90., max_value=200., value=float(p.income_growth_pct), step=0.5, key="field_income_growth")
                spending_growth = st.number_input(T("growth_expenses"), min_value=-90., max_value=200., value=float(p.expense_growth_pct), step=0.5, key="field_expense_growth")
                cash_return = st.number_input(T("cash_return"), min_value=-90., max_value=200., value=float(p.cash_return_pct), step=0.5, key="field_cash_return")
            with b:
                investment_return = st.number_input(T("investment_return"), min_value=-90., max_value=200., value=float(p.investment_return_pct), step=0.5, key="field_investment_return")
                inflation = st.number_input(T("inflation"), min_value=-90., max_value=200., value=float(p.inflation_pct), step=0.5, key="field_inflation")
                volatility = st.number_input(T("volatility"), min_value=0., max_value=100., value=float(p.investment_volatility_pct), step=1., key="field_volatility")
        with st.expander("🏡 " + T("loan_title"), expanded=False):
            a, b, c = st.columns(3, wrap=True)
            with a:
                loan = st.number_input(T("loan_balance"), min_value=0., value=float(p.loan_balance), step=step * 10, key="field_loan")
            with b:
                loan_rate = st.number_input(T("loan_apr"), min_value=0., max_value=100., value=float(p.loan_apr_pct), step=0.25, key="field_loan_rate")
            with c:
                loan_years = st.number_input(T("loan_years"), min_value=1, max_value=60, value=p.loan_years, key="field_loan_years")
            st.caption(T("loan_hint"))
        with st.expander("📅 " + T("extra_title"), expanded=False):
            previous = "\n".join(f"{e.month},{e.amount},{e.description}" for e in p.one_offs)
            oneoffs_text = st.text_area(T("extra_label"), value=previous,
                help=T("extra_hint"), key="field_oneoffs")
    else:
        income_growth, spending_growth = p.income_growth_pct, p.expense_growth_pct
        cash_return, investment_return = p.cash_return_pct, p.investment_return_pct
        inflation, volatility = p.inflation_pct, p.investment_volatility_pct
        loan, loan_rate, loan_years = p.loan_balance, p.loan_apr_pct, p.loan_years
        oneoffs_text = "\n".join(f"{e.month},{e.amount},{e.description}" for e in p.one_offs)
        st.caption(T("auto_assumptions", inflation=f"{inflation:g}", ret=f"{investment_return:g}", growth=f"{income_growth:g}"))
    enable_mc = st.checkbox(T("simulate_mc"), value=False, disabled=not advanced, key="mc_enable")
    if advanced and enable_mc:
        a, b = st.columns(2, wrap=True)
        with a:
            n_paths = st.select_slider(T("paths"), options=[250, 500, 1000, 2000, 5000], value=1000, key="mc_paths")
        with b:
            seed = st.number_input(T("seed"), min_value=0, max_value=2**31 - 1, value=42, key="mc_seed")
    else:
        n_paths, seed = 1000, 42
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
                    goal=float(goal), one_offs=parse_oneoffs(oneoffs_text, years), life_events=events)
                new_plan.validate()
                with st.spinner(T("running")):
                    result = project(new_plan)
                    mc = monte_carlo(new_plan, n_paths=int(n_paths), seed=int(seed)) if advanced and enable_mc else None
                st.session_state.plan = new_plan
                st.session_state.confirmed_inputs = True
                st.session_state.result = {"df": result, "mc": mc, "plan": new_plan}
                st.session_state.pop("goal_alternatives", None)
                st.success(T("done"))
        except (ValueError, OverflowError, ZeroDivisionError, TypeError):
            st.error(T("invalid"))

with results_tab:
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
        d.metric(T("goal_reached"), T("yes") if last.net_worth >= q.goal else T("no"))
        if (df.cash < 0).any():
            st.warning(T("negative_cash"))
        fig = go.Figure()
        for field, label, color in [("net_worth", "net_worth", "#145DA0"),
                                    ("net_worth_real", "net_worth_real", "#d97706")]:
            fig.add_trace(go.Scatter(x=df.year, y=df[field], name=T(label), line=dict(color=color)))
        fig.add_hline(y=q.goal, line_dash="dash", annotation_text=T("target_name"))
        fig.update_layout(title=T("chart_wealth"), xaxis_title=T("year"), yaxis_title=q.currency,
                          height=410, margin=dict(l=10, r=10, t=60, b=20), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, width="stretch")
        fig2 = go.Figure()
        for field, label in [("cash", "cash_name"), ("investments", "investments_name"), ("loan_balance", "loan_name")]:
            fig2.add_trace(go.Scatter(x=df.year, y=df[field], name=T(label)))
        fig2.update_layout(title=T("chart_composition"), xaxis_title=T("year"), yaxis_title=q.currency,
                           height=350, margin=dict(l=10, r=10, t=60, b=20))
        st.plotly_chart(fig2, width="stretch")
        if result["mc"] is not None:
            mc = result["mc"]
            st.subheader(T("mc_title"))
            st.caption(T("mc_hint", paths=mc.sample_paths, seed=mc.seed))
            xs = q.start_year + mc.months / 12
            fan = go.Figure()
            fan.add_trace(go.Scatter(x=xs, y=mc.p90, line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fan.add_trace(go.Scatter(x=xs, y=mc.p10, fill="tonexty", line=dict(width=0), name="P10–P90",
                                     fillcolor="rgba(20,93,160,0.17)"))
            fan.add_trace(go.Scatter(x=xs, y=mc.p50, name=T("median"), line=dict(color="#145DA0", width=3)))
            fan.update_layout(height=360, xaxis_title=T("year"), yaxis_title=q.currency)
            st.plotly_chart(fan, width="stretch")
            a, b = st.columns(2, wrap=True)
            a.metric(T("goal_probability"), f"{mc.probability_goal:.1%}")
            b.metric(T("cash_risk"), f"{mc.probability_negative_cash:.1%}")
        st.subheader(T("yearly"))
        yearly = df.iloc[::12][["year", "cash", "investments", "loan_balance", "net_worth", "net_worth_real"]]
        st.dataframe(yearly.rename(columns={"year": T("year"), "cash": T("cash_name"),
            "investments": T("investments_name"), "loan_balance": T("loan_name"),
            "net_worth": T("net_worth"), "net_worth_real": T("net_worth_real")}).round(2),
            hide_index=True, width="stretch")
        st.download_button(T("export_csv"), df.to_csv(index=False).encode("utf-8"),
                           "financial_projection_monthly.csv", mime="text/csv")
        st.caption(T("result_limit"))

with goal_tab:
    if not st.session_state.confirmed_inputs:
        st.info(T("no_result"))
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
                             + [e.month for e in reference.one_offs])
            min_years = max(1, (last_event + 11) // 12)
            horizon = st.slider(T("goal_years"), min_years, 60, max(min_years, reference.years),
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

with compare_tab:
    if not st.session_state.confirmed_inputs:
        st.info(T("no_result"))
    else:
        st.subheader(T("tab_compare"))
        st.caption(T("compare_intro"))
        base = st.session_state.plan
        shock = st.slider(T("return_shock"), min_value=0.5, max_value=10.0, value=3.0, step=0.5)
        comparison = go.Figure()
        rows = []
        scenarios = [(T("scenario_lower"), -shock, base), (T("scenario_base"), 0., base),
                     (T("scenario_higher"), shock, base)]
        if base.life_events:
            scenarios += [(T("scenario_no_events"), 0., replace(base, life_events=())),
                          (T("scenario_events_more"), 0., replace(base, life_events=tuple(
                              replace(e, monthly_expense=e.monthly_expense * 1.25,
                                      upfront_cost=e.upfront_cost * 1.25) for e in base.life_events)))]
        for name, delta, scenario in scenarios:
            scenario = replace(scenario, investment_return_pct=max(-98., min(200., scenario.investment_return_pct + delta)))
            calculated = project(scenario)
            wealth = float(calculated.net_worth.iloc[-1])
            rows.append({T("scenario_col"): name, T("return_col"): scenario.investment_return_pct,
                         T("final_col"): wealth, T("reached_col"): T("yes") if wealth >= scenario.goal else T("no")})
            comparison.add_trace(go.Scatter(x=calculated.year, y=calculated.net_worth, mode="lines", name=name))
        comparison.update_layout(height=370, xaxis_title=T("year"), yaxis_title=base.currency)
        st.plotly_chart(comparison, width="stretch")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption(T("compare_stale"))