"""Financial Adviser v0.1.0 — Streamlit UI (French, English, Vietnamese)."""
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
from financial_adviser.engine import loan_payment, monte_carlo, project
from financial_adviser.i18n import tr
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import OneOff, Plan
from financial_adviser.sources import WB_DOC, fetch_recent_inflation

st.set_page_config(page_title="Financial Adviser", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
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


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def cached_inflation(country: str) -> dict:
    try:
        return {"data": fetch_recent_inflation(country), "error": ""}
    except (OSError, ValueError, RuntimeError) as exc:
        return {"data": None, "error": str(exc)}


if "plan" not in st.session_state:
    st.session_state.plan = demo("FR")
if "result" not in st.session_state:
    st.session_state.result = None
if "pending_country" in st.session_state:
    st.session_state.country_choice = st.session_state.pop("pending_country")

with st.sidebar:
    st.title("📈 Financial Adviser")
    st.caption(f"v{__version__} · Educational simulator")
    language = st.selectbox("Language / Langue / Ngôn ngữ", ["fr", "en", "vi"],
                            format_func=lambda x: {"fr": "Français", "en": "English", "vi": "Tiếng Việt"}[x])
    if "country_choice" not in st.session_state:
        st.session_state.country_choice = st.session_state.plan.country
    country = st.selectbox(tr(language, "country"), ["FR", "VN"],
                           key="country_choice",
                           format_func=lambda c: "France (EUR)" if c == "FR" else "Việt Nam (VND)")
    if country != st.session_state.plan.country:
        st.session_state.plan = demo(country)
        st.session_state.result = None
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
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
            st.error(f"Invalid scenario: {exc}")
    st.download_button(tr(language, "download"), data=dump_plan(st.session_state.plan),
                       file_name="financial_adviser_scenario.json", mime="application/json", width="stretch")

L = lambda key: tr(language, key)
p = st.session_state.plan
st.title("Financial Adviser")
st.caption(L("subtitle"))
st.info("**Simulation pédagogique / Educational simulation / Mô phỏng tham khảo.** "
        "Les rendements et scénarios ne constituent pas des prévisions ou des conseils financiers. "
        "No automatic tax calculations; input net income after tax. Currency amounts belong to a single currency.")

tab_inputs, tab_results, tab_scenarios, tab_sources, tab_docs = st.tabs([
    "⚙️ " + L("projection"), "📊 " + L("overview"),
    "🧭 " + L("scenario"), "🔄 " + L("sources"), "📖 " + L("docs")])

with tab_inputs:
    st.subheader(L("projection"))
    st.caption("Choose a few inputs to begin; optional advanced assumptions are available using the sidebar switch.")
    with st.form("plan_form"):
        a, b, c = st.columns(3, gap="medium")
        with a:
            income = st.number_input(L("income"), min_value=0.0, value=float(p.monthly_income), step=100.0)
            expenses = st.number_input(L("expenses"), min_value=0.0, value=float(p.monthly_expenses), step=100.0)
            contribution = st.number_input(L("contribution"), min_value=0.0,
                                           value=float(p.monthly_investment), step=100.0)
        with b:
            cash = st.number_input(L("cash"), min_value=0.0, value=float(p.initial_cash), step=1000.0)
            investments = st.number_input(L("investments"), min_value=0.0,
                                          value=float(p.initial_investments), step=1000.0)
            goal = st.number_input(L("goal"), min_value=0.0, value=float(p.goal), step=1000.0)
        with c:
            years = st.slider(L("horizon"), min_value=1, max_value=60, value=p.years)
            year = st.number_input("Start year / Année de départ", min_value=2020, max_value=2100,
                                   value=p.start_year, step=1)
            st.metric("Estimated monthly free cash flow (before investment transfer)",
                      fmt(income - expenses - loan_payment(p.loan_balance, p.loan_apr_pct, p.loan_years), p.currency))
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
            new_plan = Plan(country=p.country, currency=p.currency, start_year=int(year), years=years,
                            initial_cash=cash, initial_investments=investments,
                            monthly_income=income, monthly_expenses=expenses, monthly_investment=contribution,
                            income_growth_pct=income_growth, expense_growth_pct=spending_growth,
                            cash_return_pct=cash_return, investment_return_pct=investment_return,
                            investment_volatility_pct=volatility, inflation_pct=inflation,
                            loan_balance=loan, loan_apr_pct=loan_rate, loan_years=int(loan_years),
                            goal=goal, one_offs=parse_events(events_text, years))
            new_plan.validate()
            with st.spinner("Calculs en cours / Running simulations…"):
                df = project(new_plan)
                mc = monte_carlo(new_plan, n_paths=n_paths, seed=int(seed)) if enable_mc else None
            st.session_state.plan = new_plan
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
    st.subheader("What-if comparison / Comparaison des scénarios")
    st.caption("The baseline and two return shocks use the exact same cash flows, events and inflation. They are sensitivity examples, not probability bounds.")
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
    st.plotly_chart(compare_fig, width="stretch")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption("The scenario comparison recomputes from the last saved/loaded plan; changes to the form must be submitted first.")

with tab_sources:
    st.subheader("Economic observations / Données économiques")
    auto = st.checkbox("Check annual observed inflation on app opening (cached 24 h)", value=False,
                       help="Fetches a public World Bank indicator; does not change your assumptions.")
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🔄 " + L("refresh"), width="stretch"):
            cached_inflation.clear()
            auto = True
    if auto:
        lookup = cached_inflation(st.session_state.plan.country)
        if lookup["data"] is None:
            st.warning("Source unavailable; no financial assumptions were changed. " + lookup["error"][:250])
        else:
            obs = lookup["data"]
            with col2:
                st.metric(f"World Bank annual CPI inflation — {obs['observation_year']}",
                          f"{obs['value_pct']:.2f}%")
            st.caption(f"Observation year {obs['observation_year']} · fetched {obs['retrieved_at']} UTC. This is historical, NOT a forecast.")
            st.link_button("Official data source", obs["source_url"])
            if st.button("Use this historical rate as my NEW inflation assumption (manual choice)"):
                st.session_state.plan = replace(st.session_state.plan, inflation_pct=obs["value_pct"])
                st.session_state.result = None
                st.rerun()
    st.markdown(f"[World Bank API methodology]({WB_DOC})")
    st.divider()
    st.subheader("Regulatory references / Références réglementaires")
    catalogue = json.loads((ROOT / "rules" / "catalogue.json").read_text(encoding="utf-8"))
    st.caption(f"Catalogue checked: {catalogue['checked_on']} · Regulations are NOT automatically applied or updated by this version.")
    for entry in catalogue["entries"]:
        with st.expander(f"{entry['country']} · {entry['id']} · {entry['status']}"):
            st.write(entry["notes"])
            st.write(f"Effective from: {entry['effective_from']}")
            st.link_button("Official legal source", entry["source_url"])
    st.warning("Legal texts can change. v0.1.0 does not parse, activate, or calculate tax rules automatically. Check the official source before a real decision.")

with tab_docs:
    st.subheader("Method and scope / Méthode et périmètre")
    st.markdown("""
- **Income:** already net of taxes and social contributions. It grows at an assumed effective annual rate.
- **Spending:** excludes loan repayments and savings transfers, which are accounted for separately.
- **Investment transfer:** moves cash into investments; it is not a new income stream.
- **Debt:** an outstanding fixed-rate amortizing loan. Repayments include interest; no corresponding real-estate asset is inferred.
- **Cash shortfall:** allowed in the model to expose an unsustainable plan; overdraft costs are excluded.
- **Inflation:** converts nominal net worth into constant purchasing-power terms at the scenario start date.
- **Monte Carlo:** independent normally distributed monthly investment returns, fixed cash yield and inflation. Not a calibrated market forecast.
- **Fiscality:** no automatic tax calculation, tax relief, social contributions, pension or cross-border treatment in this version.
- **Confidentiality:** no bank connection or built-in account. A public Streamlit deployment **processes entries on its server**; do not enter sensitive real data on an untrusted instance.
""")
    st.markdown("The full project specification, source registry, formulas, architecture, roadmap and decision log are in the [`Documentation/`](https://github.com/trungtin-dinh/financial_adviser/tree/main/Documentation) folder.")
    st.markdown("[AMF — past performance is not a forecast](https://www.amf-france.org/fr/espace-epargnants/savoir-bien-investir/cadrer-son-projet/les-performances-passees-ne-prejugent-pas-des-performances-futures-pourquoi-cette-mention-0)")
    st.caption("Open source education project. Not personal investment, legal or tax advice.")
