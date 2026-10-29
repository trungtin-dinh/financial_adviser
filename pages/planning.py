"""Financial Adviser planning interface; methods and sources are separate pages."""
from __future__ import annotations

import csv
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_adviser import __version__
from financial_adviser.engine import loan_payment, monte_carlo, project, solve_goal
from financial_adviser.i18n import tr
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import OneOff, LifeEvent, Plan

ROOT = Path(__file__).resolve().parent


def demo(country: str) -> Plan:
    if country == "VN":
        return Plan(country="VN", currency="VND", initial_cash=150_000_000,
                    initial_investments=250_000_000, monthly_income=50_000_000,
                    monthly_expenses=30_000_000, monthly_investment=10_000_000,
                    goal=2_000_000_000)
    return Plan()


def fmt(amount: float, currency: str) -> str:
    decimals = 0 if currency == "VND" else 2
    s = f"{amount:,.{decimals}f}".replace(",", " ")
    return f"{s} {'₫' if currency == 'VND' else '€'}"


def parse_events(raw: str, years: int) -> tuple[OneOff, ...]:
    if not raw.strip():
        return ()
    rows = list(csv.reader(StringIO(raw), skipinitialspace=True))
    if len(rows) > 100:
        raise ValueError("Maximum 100 events")
    out = []
    for i, row in enumerate(rows, start=1):
        if not row or not any(part.strip() for part in row):
            continue
        if len(row) not in (2, 3):
            raise ValueError(f"Line {i}: expected month,amount[,description]")
        month = int(row[0].strip())
        amount = float(row[1].strip())
        event = OneOff(month=month, amount=amount,
                       description=row[2].strip() if len(row) == 3 else "")
        out.append(event)
    return tuple(out)


if "plan" not in st.session_state:
    st.session_state.plan = demo("FR")
if "result" not in st.session_state:
    st.session_state.result = None
if "confirmed_inputs" not in st.session_state:
    st.session_state.confirmed_inputs = False
if "pending_country" in st.session_state:
    st.session_state.country_choice = st.session_state.pop("pending_country")

with st.sidebar:
    st.title("📈 Financial Adviser")
    st.caption(f"v{__version__} · Educational simulator")
    language = st.selectbox("Language / Langue / Ngôn ngữ", ["fr", "en", "vi"],
                            key="language_choice", format_func=lambda x: {"fr": "Français", "en": "English", "vi": "Tiếng Việt"}[x])
    if "country_choice" not in st.session_state:
        st.session_state.country_choice = st.session_state.plan.country
    country = st.selectbox(tr(language, "country"), ["FR", "VN"],
                           key="country_choice",
                           format_func=lambda c: "France (EUR)" if c == "FR" else "Việt Nam (VND)")
    if country != st.session_state.plan.country:
        st.session_state.plan = demo(country)
        st.session_state.result = None
        st.session_state.confirmed_inputs = False
        st.session_state.pop("life_events_editor", None)
        st.session_state.pop("goal_alternatives", None)
        st.info("Example reset for the selected currency. No automatic FX conversion.")
    advanced = st.toggle(tr(language, "advanced"), value=False)
    st.caption("No bank connection. Inputs are stored in the current Streamlit session; uploaded files are processed by the app server.")
    st.divider()
    uploaded = st.file_uploader(tr(language, "import"), type=["json"], max_upload_size=1)
    if uploaded is not None and st.button("Load / Charger / Tải", width="stretch"):
        try:
            imported = load_plan(uploaded.getvalue())
            st.session_state.plan = imported
            st.session_state.pending_country = imported.country
            st.session_state.result = None
            st.session_state.confirmed_inputs = True
            st.session_state.pop("life_events_editor", None)
            st.session_state.pop("goal_alternatives", None)
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            st.error(f"Invalid scenario: {exc}")
    if st.button("📋 " + {"fr": "Charger un exemple", "en": "Load example", "vi": "Dùng số liệu mẫu"}.get(language, "Load example"), width="stretch"):
        st.session_state.plan = demo(st.session_state.plan.country)
        st.session_state.confirmed_inputs = True
        st.session_state.result = None
        st.session_state.pop("life_events_editor", None)
        st.session_state.pop("goal_alternatives", None)
        st.rerun()
    st.download_button(tr(language, "download"), data=dump_plan(st.session_state.plan),
                       file_name="financial_adviser_scenario.json", mime="application/json", width="stretch")

L = lambda key: tr(language, key)
p = st.session_state.plan
st.title("Financial Adviser")
st.caption(L("subtitle"))
st.info("**Simulation pédagogique / Educational simulation / Mô phỏng tham khảo.** "
        "Les rendements et scénarios ne constituent pas des prévisions ou des conseils financiers. "
        "No automatic tax calculations; input net income after tax. Currency amounts belong to a single currency.")

tab_inputs, tab_results, tab_goal, tab_scenarios = st.tabs([
    "⚙️ " + L("projection"), "📊 " + L("overview"),
    "🎯 " + {"fr": "Objectif à atteindre", "en": "Goal seek", "vi": "Tìm cách đạt mục tiêu"}.get(language, "Goal seek"),
    "🧭 " + L("scenario")])

with tab_inputs:
    st.subheader(L("projection"))
    st.caption({"fr": "Saisissez les valeurs essentielles. Les autres hypothèses sont proposées et restent modifiables dans le mode avancé.",
                "en": "Enter the essential values; optional assumptions are editable in Advanced mode.",
                "vi": "Nhập các giá trị quan trọng; các giả định khác có thể chỉnh trong chế độ Nâng cao."}[language])
    if not st.session_state.confirmed_inputs:
        st.warning({"fr": "Les champs essentiels sont volontairement vides. Renseignez vos valeurs, ou chargez l'exemple via le menu latéral.",
                    "en": "Required inputs start empty. Enter your figures, or load the sidebar example.",
                    "vi": "Thông số bắt buộc được để trống. Hãy nhập số liệu hoặc tải ví dụ từ thanh bên."}[language])
    with st.form("plan_form"):
        a, b, c = st.columns(3, gap="medium")
        with a:
            income = st.number_input(L("income"), min_value=0.0, value=float(p.monthly_income) if st.session_state.confirmed_inputs else None, step=100.0, placeholder="Required / Obligatoire")
            expenses = st.number_input(L("expenses"), min_value=0.0, value=float(p.monthly_expenses) if st.session_state.confirmed_inputs else None, step=100.0, placeholder="Required / Obligatoire")
            contribution = st.number_input(L("contribution"), min_value=0.0,
                                           value=float(p.monthly_investment) if st.session_state.confirmed_inputs else 0.0, step=100.0)
        with b:
            cash = st.number_input(L("cash"), min_value=0.0, value=float(p.initial_cash) if st.session_state.confirmed_inputs else 0.0, step=1000.0)
            investments = st.number_input(L("investments"), min_value=0.0,
                                          value=float(p.initial_investments) if st.session_state.confirmed_inputs else 0.0, step=1000.0)
            goal = st.number_input(L("goal"), min_value=0.0, value=float(p.goal) if st.session_state.confirmed_inputs else None, step=1000.0, placeholder="Required / Obligatoire")
        with c:
            years = st.slider(L("horizon"), min_value=1, max_value=60, value=p.years)
            year = st.number_input("Start year / Année de départ", min_value=2020, max_value=2100,
                                   value=p.start_year, step=1)
            st.metric("Estimated monthly free cash flow (before investment transfer)",
                      fmt((income or 0) - (expenses or 0) - loan_payment(p.loan_balance, p.loan_apr_pct, p.loan_years), p.currency))
        with st.expander("👨‍👩‍👧‍👦 " + {"fr": "Événements de vie et risques (facultatif)", "en": "Life events and risks (optional)", "vi": "Sự kiện cuộc sống và rủi ro (không bắt buộc)"}[language], expanded=False):
            st.caption({"fr": "Enfant, maladie, perte d'emploi, déménagement, achat important… Chaque ligne est une hypothèse explicite, pas une probabilité médicale. Les dépenses supplémentaires sont POSITIVES ; la variation du revenu peut être négative.",
                        "en": "Child, illness, unemployment, relocation, major purchase… Enter explicit hypothetical costs, not medical probabilities. Extra expenses are POSITIVE; income changes may be negative.",
                        "vi": "Con cái, bệnh tật, thất nghiệp, chuyển nhà, mua sắm lớn… Điền chi phí giả định; không dự đoán xác suất bệnh. Chi thêm là số DƯƠNG; thay đổi thu nhập có thể âm."}[language])
            event_cols = ["category", "label", "first_month", "duration_months", "monthly_expense", "monthly_income_change", "upfront_cost"]
            event_rows = [vars(x) for x in p.life_events]
            event_table = st.data_editor(pd.DataFrame(event_rows, columns=event_cols),
                num_rows="dynamic", hide_index=True, width="stretch", key="life_events_editor",
                column_config={
                    "category": st.column_config.SelectboxColumn("Type", options=["Child / Dependent", "Health / Care", "Large purchase", "Unemployment", "Education", "Relocation", "Other"], required=True),
                    "label": st.column_config.TextColumn("Description", required=True),
                    "first_month": st.column_config.NumberColumn("Start month", min_value=1, max_value=720, step=1, required=True),
                    "duration_months": st.column_config.NumberColumn("Duration (months)", min_value=1, max_value=720, step=1, required=True),
                    "monthly_expense": st.column_config.NumberColumn("Extra monthly cost", min_value=0., step=100.),
                    "monthly_income_change": st.column_config.NumberColumn("Monthly income change", step=100.),
                    "upfront_cost": st.column_config.NumberColumn("Initial purchase / cost", min_value=0., step=100.)})
            st.caption("A child or an illness is not modeled as a random forecast. Add one or more dated assumptions to compare their impact.")
        if advanced:
            with st.expander("📐 Hypothèses / Assumptions / Giả định", expanded=True):
                aa, bb, cc = st.columns(3)
                with aa:
                    income_growth = st.number_input(L("growth_income"), min_value=-90.0, max_value=200.0,
                                                    value=float(p.income_growth_pct), step=0.5)
                    spending_growth = st.number_input(L("growth_expenses"), min_value=-90.0, max_value=200.0,
                                                      value=float(p.expense_growth_pct), step=0.5)
                with bb:
                    cash_return = st.number_input(L("cash_return"), min_value=-90.0, max_value=200.0,
                                                  value=float(p.cash_return_pct), step=0.5)
                    investment_return = st.number_input(L("return"), min_value=-90.0, max_value=200.0,
                                                        value=float(p.investment_return_pct), step=0.5)
                with cc:
                    inflation = st.number_input(L("inflation"), min_value=-90.0, max_value=200.0,
                                                value=float(p.inflation_pct), step=0.5)
                    volatility = st.number_input(L("volatility"), min_value=0.0, max_value=100.0,
                                                 value=float(p.investment_volatility_pct), step=1.0)
            with st.expander("🏡 Debt / Crédit / Vay", expanded=False):
                loan = st.number_input(L("loan"), min_value=0.0, value=float(p.loan_balance), step=1000.0)
                loan_rate = st.number_input(L("loan_rate"), min_value=0.0, max_value=100.0,
                                            value=float(p.loan_apr_pct), step=0.25)
                loan_years = st.number_input(L("loan_years"), min_value=1, max_value=60,
                                             value=p.loan_years)
                st.caption("Monthly loan payments are deducted from cash flow. Exclude these payments from ordinary expenses. Property value is not inferred.")
            with st.expander("📅 Events / Événements / Sự kiện", expanded=False):
                previous = "\n".join(f"{e.month},{e.amount},{e.description}" for e in p.one_offs)
                events_text = st.text_area(L("events"), value=previous,
                                           placeholder="12,-5000,car purchase\n24,2000,bonus", height=100)
        else:
            income_growth, spending_growth = p.income_growth_pct, p.expense_growth_pct
            cash_return, investment_return = p.cash_return_pct, p.investment_return_pct
            inflation, volatility = p.inflation_pct, p.investment_volatility_pct
            loan, loan_rate, loan_years = p.loan_balance, p.loan_apr_pct, p.loan_years
            events_text = "\n".join(f"{e.month},{e.amount},{e.description}" for e in p.one_offs)
            st.caption(f"Default assumptions: inflation {inflation:g}%/year · investment return {investment_return:g}%/year · salary growth {income_growth:g}%/year. Switch to Advanced to edit them.")
        enable_mc = st.checkbox(L("mc"), value=advanced, disabled=not advanced)
        n_paths = st.select_slider(L("paths"), options=[250, 500, 1000, 2000, 5000], value=1000,
                                   disabled=not (advanced and enable_mc))
        seed = st.number_input(L("seed"), min_value=0, max_value=2**31 - 1, value=42,
                               disabled=not (advanced and enable_mc))
        run = st.form_submit_button("▶ " + L("run"), type="primary", width="stretch")
    if run:
        try:
            if income is None or expenses is None or goal is None:
                raise ValueError("Please fill net income, monthly spending and target. / Renseignez les champs obligatoires.")
            life_events = []
            for row in event_table.to_dict("records"):
                if not row.get("category") or not row.get("label"):
                    raise ValueError("Each life event needs a category and description.")
                def number(key, default=0.):
                    v = row.get(key)
                    return default if v is None or pd.isna(v) else float(v)
                life_events.append(LifeEvent(category=str(row["category"]), label=str(row["label"]),
                    first_month=int(number("first_month")), duration_months=int(number("duration_months")),
                    monthly_expense=number("monthly_expense"),
                    monthly_income_change=number("monthly_income_change"), upfront_cost=number("upfront_cost")))
            if len(life_events) > 100:
                raise ValueError("Maximum 100 life events")
            new_plan = Plan(country=p.country, currency=p.currency, start_year=int(year), years=years,
                            initial_cash=cash, initial_investments=investments,
                            monthly_income=income, monthly_expenses=expenses, monthly_investment=contribution,
                            income_growth_pct=income_growth, expense_growth_pct=spending_growth,
                            cash_return_pct=cash_return, investment_return_pct=investment_return,
                            investment_volatility_pct=volatility, inflation_pct=inflation,
                            loan_balance=loan, loan_apr_pct=loan_rate, loan_years=int(loan_years),
                            goal=goal, one_offs=parse_events(events_text, years),
                            life_events=tuple(life_events))
            new_plan.validate()
            with st.spinner("Calculs en cours / Running simulations…"):
                df = project(new_plan)
                mc = monte_carlo(new_plan, n_paths=n_paths, seed=int(seed)) if enable_mc else None
            st.session_state.plan = new_plan
            st.session_state.confirmed_inputs = True
            st.session_state.pop("goal_alternatives", None)
            st.session_state.result = {"df": df, "mc": mc, "plan": new_plan}
            st.success("✓ Projection terminée. Open the Results tab to inspect the charts and exports.")
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            st.error(f"Invalid inputs: {exc}")

with tab_results:
    result = st.session_state.result
    if result is None:
        st.info("Run a projection in the first tab to see results.")
    else:
        q: Plan = result["plan"]
        df: pd.DataFrame = result["df"]
        last = df.iloc[-1]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Net worth / Patrimoine net", fmt(float(last.net_worth), q.currency))
        k2.metric("Purchasing-power adjusted", fmt(float(last.net_worth_real), q.currency))
        k3.metric("Remaining loan", fmt(float(last.loan_balance), q.currency))
        k4.metric("Goal reached (deterministic)", "Yes / Oui" if last.net_worth >= q.goal else "No / Non")
        if (df["cash"] < 0).any():
            st.warning("The cash balance becomes negative. This models an **unfunded cash shortfall**, not an authorized overdraft; borrowing costs are not included.")
        fig = go.Figure()
        for name, color in [("net_worth", "#145DA0"), ("net_worth_real", "#d97706")]:
            fig.add_trace(go.Scatter(x=df["year"], y=df[name], mode="lines",
                                     name={"net_worth": "Nominal net worth", "net_worth_real": "Real net worth"}[name],
                                     line=dict(color=color)))
        fig.add_hline(y=q.goal, line_dash="dash", annotation_text="Target (nominal)")
        fig.update_layout(title="Net worth projection (monthly calculation)", xaxis_title="Year",
                          yaxis_title=q.currency, height=430, margin=dict(l=20, r=20, t=60, b=20),
                          legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig, width="stretch")
        components = go.Figure()
        for key, label in [("cash", "Cash"), ("investments", "Investments"), ("loan_balance", "Outstanding loan")]:
            components.add_trace(go.Scatter(x=df["year"], y=df[key], name=label, mode="lines"))
        components.update_layout(title="Assets and liabilities", xaxis_title="Year", yaxis_title=q.currency,
                                 height=350, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(components, width="stretch")
        if result["mc"] is not None:
            mc = result["mc"]
            st.subheader("Monte Carlo — illustrative distribution")
            st.caption(f"{mc.sample_paths:,} independent simulated paths; seed={mc.seed}. "
                       "10th–90th percentile band. Normal IID investment returns; inflation and cash returns fixed. No taxes, fees, or asset correlations.")
            mcf = go.Figure()
            xs = q.start_year + mc.months / 12
            mcf.add_trace(go.Scatter(x=xs, y=mc.p90, mode="lines", line=dict(width=0),
                                     showlegend=False, hoverinfo="skip"))
            mcf.add_trace(go.Scatter(x=xs, y=mc.p10, mode="lines", fill="tonexty",
                                     fillcolor="rgba(20,93,160,0.17)", line=dict(width=0),
                                     name="P10–P90"))
            mcf.add_trace(go.Scatter(x=xs, y=mc.p50, mode="lines", name="Median P50",
                                     line=dict(color="#145DA0", width=3)))
            mcf.update_layout(height=390, xaxis_title="Year", yaxis_title=q.currency)
            st.plotly_chart(mcf, width="stretch")
            mm1, mm2 = st.columns(2)
            mm1.metric("P(final net worth ≥ target)", f"{mc.probability_goal:.1%}")
            mm2.metric("P(cash shortfall at least once)", f"{mc.probability_negative_cash:.1%}")
        yearly = df.iloc[::12].copy()
        st.dataframe(yearly[["year", "cash", "investments", "loan_balance", "net_worth", "net_worth_real"]]
                     .round(2), hide_index=True, width="stretch")
        st.download_button("⬇ Export monthly CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name="financial_projection_monthly.csv", mime="text/csv")
        st.caption("Tax, pension, asset-specific rules and real estate valuation are not yet calculated. Results are estimates only.")

with tab_scenarios:
    if not st.session_state.confirmed_inputs:
        st.info("Enter the essential fields in Plan first, or load the explicit example.")
    else:
        st.subheader("What-if comparison / Comparaison des scénarios")
        st.caption("Return shocks and life-event stress variants are hypothetical sensitivity tests, NOT probability bounds.")
        base = st.session_state.plan
        shock = st.slider("Return shock (+/− percentage points per year)", min_value=0.5,
                          max_value=10.0, value=3.0, step=0.5)
        rows = []
        compare_fig = go.Figure()
        for label, delta in [("Lower", -shock), ("Baseline", 0), ("Higher", shock)]:
            altered = replace(base, investment_return_pct=max(-98.0, min(200.0, base.investment_return_pct + delta)))
            sdf = project(altered)
            rows.append({"Scenario": label, "Annual investment return (%)": altered.investment_return_pct,
                         "Final net worth": float(sdf.net_worth.iloc[-1]), "Goal reached": bool(sdf.net_worth.iloc[-1] >= altered.goal)})
            compare_fig.add_trace(go.Scatter(x=sdf.year, y=sdf.net_worth,
                                             mode="lines", name=label))
        compare_fig.update_layout(height=370, xaxis_title="Year", yaxis_title=base.currency)
        if base.life_events:
            for label, alternative in [
                ("Without modeled life events", replace(base, life_events=())),
                ("Life event costs +25%", replace(base, life_events=tuple(
                    replace(e, monthly_expense=e.monthly_expense * 1.25,
                            upfront_cost=e.upfront_cost * 1.25) for e in base.life_events)))]:
                sdf = project(alternative)
                rows.append({"Scenario": label, "Annual investment return (%)": alternative.investment_return_pct,
                             "Final net worth": float(sdf.net_worth.iloc[-1]),
                             "Goal reached": bool(sdf.net_worth.iloc[-1] >= alternative.goal)})
                compare_fig.add_trace(go.Scatter(x=sdf.year, y=sdf.net_worth, mode="lines", name=label))
        st.plotly_chart(compare_fig, width="stretch")
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.caption("The scenario comparison recomputes from the last saved/loaded plan; changes to the form must be submitted first.")

with tab_goal:
    if not st.session_state.confirmed_inputs:
        st.info("Complete your initial plan first, or explicitly load the example from the sidebar.")
    else:
        st.subheader({"fr": "Partir d'un résultat souhaité", "en": "Work backward from your goal", "vi": "Tính ngược từ mục tiêu"}[language])
        st.caption({"fr": "Modifiez la sortie souhaitée : l'application propose plusieurs modifications INDÉPENDANTES des entrées. Les propositions doivent également éviter toute trésorerie négative.",
                    "en": "Change the desired output: compare INDEPENDENT input changes, each constrained to avoid negative cash.",
                    "vi": "Đặt kết quả mong muốn; ứng dụng tính các thay đổi đầu vào ĐỘC LẬP, đồng thời tránh thiếu hụt tiền mặt."}[language])
        reference = st.session_state.plan
        c1, c2 = st.columns(2)
        with c1:
            target = st.number_input({"fr": "Patrimoine net nominal ciblé", "en": "Nominal net worth target", "vi": "Mục tiêu tài sản ròng danh nghĩa"}[language], min_value=0., value=float(reference.goal), step=1000.)
        with c2:
            latest_event = max([0] + [e.first_month + e.duration_months - 1 for e in reference.life_events]
                               + [e.month for e in reference.one_offs])
            min_years = max(1, (latest_event + 11) // 12)
            hgoal = st.slider({"fr": "Horizon cible (années)", "en": "Target horizon (years)", "vi": "Số năm để đạt mục tiêu"}[language], min_years, 60, max(min_years, reference.years))
        if st.button({"fr": "Calculer les moyens nécessaires", "en": "Find feasible alternatives", "vi": "Tính các phương án khả thi"}[language], type="primary", width="stretch"):
            try:
                alternatives = solve_goal(reference, float(target), hgoal)
                st.session_state.goal_alternatives = alternatives
                st.session_state.goal_query = (reference, float(target), int(hgoal))
            except (ValueError, OverflowError) as exc:
                st.error(str(exc))
        if "goal_alternatives" in st.session_state:
            if st.session_state.get("goal_query") != (reference, float(target), int(hgoal)):
                st.info("Inputs have changed. Click 'Find feasible alternatives' to refresh these estimates.")
            alternatives = st.session_state.goal_alternatives
            titles = {
                "income": {"fr": "Revenu net mensuel supplémentaire", "en": "Extra net monthly income", "vi": "Thu nhập ròng tăng mỗi tháng"},
                "expenses": {"fr": "Réduction des dépenses mensuelles", "en": "Monthly spending reduction", "vi": "Giảm chi tiêu mỗi tháng"},
                "capital": {"fr": "Apport initial externe", "en": "External initial capital", "vi": "Vốn bổ sung ban đầu"},
            }
            for i, option in enumerate(alternatives):
                with st.container(border=True):
                    st.markdown("**" + titles[option.lever][language] + "**")
                    if not option.feasible:
                        st.warning({"fr": "Non réalisable avec ce seul levier", "en": "Not feasible with this lever alone", "vi": "Không khả thi chỉ với phương án này"}[language])
                        st.caption(option.explanation)
                    else:
                        st.metric("Required / Requis", fmt(option.amount, reference.currency))
                        preview = project(option.scenario)
                        st.caption(f"Result: {fmt(float(preview.net_worth.iloc[-1]), reference.currency)} · Minimum cash: {fmt(float(preview.cash.min()), reference.currency)}")
                        if st.button({"fr": "Utiliser ce scénario", "en": "Use this scenario", "vi": "Sử dụng phương án"}[language], key=f"apply_solution_{i}",
                                     disabled=st.session_state.get("goal_query") != (reference, float(target), int(hgoal))):
                            st.session_state.plan = option.scenario
                            st.session_state.confirmed_inputs = True
                            st.session_state.result = {"df": preview, "mc": None, "plan": option.scenario}
                            del st.session_state.goal_alternatives
                            st.session_state.pop("life_events_editor", None)
                            st.rerun()
            st.caption({"fr": "Les trois options sont séparées, non cumulatives. Les rendements, la fiscalité et les probabilités d'événements ne sont pas optimisés.",
                        "en": "Alternatives are separate, not additive. Market returns, taxes and event probabilities are not optimized.",
                        "vi": "Các phương án độc lập, không cộng dồn. Không tối ưu lợi suất thị trường, thuế hay xác suất sự kiện."}[language])
