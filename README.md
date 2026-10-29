# Financial Adviser

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-v0.1.0_MVP-yellow)](Documentation/07_ROADMAP.md)

**Educational financial scenario simulator** for desktop browsers, with a responsive Streamlit interface and initial France / Vietnam presets. Designed to become an extensible, source-traceable financial planning platform.

**Simulate, compare and explain — without implying that a model predicts the future.**

> **Important:** This is a first usable **MVP**, not an investment adviser, tax calculator, account aggregator, or forecast of future asset returns. Default rates and income amounts are *illustrative assumptions*, not market estimates or personalized recommendations. Avoid entering confidential data in deployments you do not control.

## Features in v0.1.0

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

Open the local address printed by Streamlit (usually `http://localhost:8501`). A modern browser is required. The app is intended primarily for desktop use; narrow screens are supported through responsive layout, but full mobile usability still requires device testing.

### Tests

```bash
pip install -e '.[dev]'
pytest -q
```

### Recommended first use

1. Choose **France (EUR)** or **Việt Nam (VND)** on the left. Switching countries resets the example amounts; it does **not** convert the old currency values.
2. Enter **net monthly income**, monthly spending **excluding loan payments**, initial cash, investments and monthly transfers.
3. Select a duration and target; click **Run projection**.
4. Inspect charts and download CSV in **Results**, then compare alternate assumed investment returns in **Scenarios**.
5. Switch to **Advanced** for volatility, return rates, loan assumptions and one-off events.
6. Export the scenario JSON to save it; browser session state is not permanent storage.

A public Streamlit server processes form data on the host server; local launching is recommended for private information. The repository does not offer a login, bank API connection, or server-side personal-profile database.

## Calculation boundaries

- Taxation, social insurance, pensions, tax wrappers (PEA/PER/etc.), cross-border tax treaties and legal compliance are **not modeled** in v0.1.0. Enter income already **net** of salary-related deductions. Investment returns are modeled **before any specific investment tax or fee**.
- Debt represents **outstanding principal** and not a property acquisition. Enter a matching property asset only when a future real-estate module supports it; otherwise debt reduces model net worth.
- Negative cash values indicate an **unfunded shortfall**, not an approved overdraft; overdraft costs are not calculated.
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

Documentation is primarily in French; the app UI provides FR/EN/VI controls and core terminology.

## License

No project license has been selected yet. The source is visible on GitHub, but it is **not automatically licensed for redistribution** until a license is added. The reference applications cited in the docs have their own independent licenses; this project does not copy their source code.
