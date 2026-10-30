# Financial Adviser

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-v0.3.0_MVP-yellow)](Documentation/07_ROADMAP.md)

**Educational financial scenario simulator** for desktop browsers, with a responsive Streamlit interface and initial France / Vietnam presets. Designed to become an extensible, source-traceable financial planning platform.

**Simulate, compare and explain — without implying that a model predicts the future.**

> **Important:** This is a first usable **MVP**, not an investment adviser, tax calculator, account aggregator, or forecast of future asset returns. Default rates and income amounts are *illustrative assumptions*, not market estimates or personalized recommendations. Avoid entering confidential data in deployments you do not control.

## Features in v0.3.0

- **Unified display language:** interface strings, navigation and charts follow a single language (FR/EN/VI). Technical reference documents are explicitly identified as French originals.
- **Responsive event cards:** individual life events replace the former seven-column editor; each card has date, duration, recurring costs, income change and upfront cost.
- **Automated UX checks:** browser screenshots and overflow assertions for desktop, tablet and mobile viewports.


- **Life events and personal disruptions:** optional dated changes to income and expenses and one-time costs, such as childcare, care obligations, unemployment or major purchases. The app does not estimate their likelihood.
- **Goal-seeking / reverse simulation:** set target net worth and horizon, compute three separate conditional alternatives (additional net income, lower baseline spending or additional external capital) while enforcing non-negative projected cash.
- **Progressive disclosure:** income, spending and goal must be entered at first use (or explicitly load the example); remaining assumptions use transparent, editable defaults.
- **Separate documentation pages:** financial setup and calculations live in Plan & Simulations, technical reference in Guide & Models, economic and regulatory sources in Sources & Regulations.
- Monthly, deterministic simulation of income, spending, cash, investments, savings transfers and net worth for up to 60 years.
- Growth of income and spending, effective monthly investment returns and inflation-adjusted net worth.
- Optional outstanding fixed-rate amortizing loan: debt repayments affect cash flow; no property asset is invented.
- One-time dated cash events, e.g. a repair, bonus, or home down-payment.
- Monte Carlo simulation with a configurable annualized volatility, path count and reproducible seed; P10/P50/P90 and illustrative target attainment probability.
- Return shock comparison (baseline, higher, lower), interactive Plotly charts and annual results table.
- Import/export versioned JSON scenarios and export monthly results as CSV.
- Language controls for French, English and Vietnamese; country presets in EUR/VND (no automatic foreign-exchange conversion yet).
- Optional manual/opt-in fetch of **historical** inflation observations from the [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392), with a 24-hour Streamlit cache. The data does not silently overwrite scenario assumptions.
- A sourced regulatory-reference catalogue that does **not** execute fiscal calculations.

## Run locally

```bash
# Python 3.11+ recommended
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit (usually `http://localhost:8501`). A modern browser is required. The app is intended primarily for desktop use; desktop/tablet/mobile viewports are covered by automated Chromium tests; physical-device evaluation remains a separate task.

### Tests

```bash
pip install -e '.[dev]'
pytest -q
```

### Recommended first use

1. Choose **France (EUR)** or **Việt Nam (VND)** on the left. Currency switching resets example assumptions; it does **not** convert values.
2. Enter the **required** net income, monthly spending and nominal target, plus a horizon. Load the sample explicitly if preferred; initial cash, investments and monthly transfers are optional.
3. Select a duration and target; click **Run projection**.
4. Inspect charts and CSV in **Results**, use **Goal seek** to work backward from a desired output, and compare alternate returns / life-event costs in **Scenarios**.
5. Add optional **Life events** (child, care, unemployment, major purchase) in the collapsible editor; switch to **Advanced** for volatility, return rates, loan assumptions and detailed one-off flows.
6. Export the scenario JSON to save it; browser session state is not permanent storage.

A public Streamlit server processes form data on the host server; local launching is recommended for private information. The repository does not offer a login, bank API connection, or server-side personal-profile database.

## Calculation boundaries

- Taxation, social insurance, pensions, tax wrappers (PEA/PER/etc.), cross-border tax treaties and legal compliance are **not modeled** in v0.3.0. Enter income already **net** of salary-related deductions. Investment returns are modeled **before any specific investment tax or fee**.
- Debt represents **outstanding principal** and not a property acquisition. Enter a matching property asset only when a future real-estate module supports it; otherwise debt reduces model net worth.
- Negative cash values indicate an **unfunded shortfall**, not an approved overdraft; overdraft costs are not calculated.
- Life events are user-defined **deterministic scenario assumptions**, not risk probabilities; this version does not infer healthcare expenses, benefits, medical outcomes or family decisions.
- Goal-seek solves one lever at a time for nominal ending net worth, while demanding non-negative cash every projected month. It does **not** optimize taxation, likelihood, or combinations of levers.
- The Monte Carlo model is deliberately simple (independent normal investment returns with a -99% lower clipping bound, constant inflation, no correlations); its probabilities are **conditional on assumptions**, not calibrated likelihoods.
- Annual returns used by the cash/investment engine are *effective* rates; borrowing APR is a *nominal* annual rate with monthly interest APR/12. Values are calculated monthly and one-off events occur before monthly returns.

## Documentation

All design decisions, equations, official references, specification and future work are stored in **[`Documentation/`](Documentation/00_INDEX.md)**:

- [Vision and specifications](Documentation/01_CAHIER_DES_CHARGES.md)
- [Equations and conventions](Documentation/02_MODELES_MATHEMATIQUES.md)
- [Economics, legal sources and updates](Documentation/03_SOURCES_ET_REGLES.md)
- [Architecture and data contracts](Documentation/04_ARCHITECTURE.md)
- [Existing-app research](Documentation/05_BENCHMARK.md)
- [Quality, privacy and limitations](Documentation/06_QUALITE_ET_LIMITES.md)
- [Roadmap](Documentation/07_ROADMAP.md)
- [Decision journal](Documentation/08_JOURNAL.md)
- [Life events, inverse planning, usability and simulated-persona audit](Documentation/09_FACTEURS_DE_VIE_ET_UX.md)
- [Responsive UI and localization audit](Documentation/10_ERGONOMIE_RESPONSIVE_ET_LANGUES.md)
- [Statistical default profiles: research and implementation constraints](Documentation/11_PROFILS_STATISTIQUES.md)

Technical documentation remains primarily in French; interface controls, messages, charts and navigation are localized consistently in French, English or Vietnamese.

## License

No project license has been selected yet. The source is visible on GitHub, but it is **not automatically licensed for redistribution** until a license is added. The reference applications cited in the docs have their own independent licenses; this project does not copy their source code.
