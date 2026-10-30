# Financial Adviser

**[🌐 Open the live Streamlit app](https://financial-adviser.streamlit.app/)** · [Source code](https://github.com/trungtin-dinh/financial_adviser) · [Documentation](Documentation/00_INDEX.md)

[![Live Streamlit app](https://img.shields.io/badge/Live_app-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://financial-adviser.streamlit.app/)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-web_app-red)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-v0.7.0_household_candidate-yellow)](Documentation/07_ROADMAP.md)

**Educational financial scenario simulator** for desktop browsers, with a responsive Streamlit interface and initial France / Vietnam presets. Designed to become an extensible, source-traceable financial planning platform.

**Simulate, compare and explain — without implying that a model predicts the future.**

> **Important:** This is a first usable **MVP**, not an investment adviser, tax calculator, account aggregator, or forecast of future asset returns. Default rates and income amounts are *illustrative assumptions*, not market estimates or personalized recommendations. Avoid entering confidential data in deployments you do not control.

## Features in v0.7.0

- **Household life-cycle model:** optional children aged from 0 to up to 30; age-specific living and childcare/education monthly budgets, configurable age when support ends (illustrative default 25), future births and several children.
- **Avoid double counting:** each current child can be marked as already included in the household's current spending. The projection then includes only future changes, and releases that part of the original budget when financial support ends.
- **Adults' finances across the life cycle:** age-dependent discretionary monthly expense adjustments, income-share allocation between adults (up to 100% combined), and an explicitly hypothetical retirement transition. No automatic legal pension/tax/health estimate.
- **Year-by-year finances:** child/adult spending and retirement income are reflected in baseline projection, Monte Carlo and goal-seek, with dedicated signed-change chart. Legacy saved scenarios remain supported.
- **No official average child cost assumed:** all starter values are synthetic and user-editable. Country-specific research is documented with DREES, Insee, IRES, NSO and OECD references.


- **Six editable event templates:** income interruption, healthcare, emergency expense, childcare, family support and relocation. All proposed values are synthetic proportions of your own budget, never official medians or personalized probabilities. Events are added only on confirmation, then remain fully editable.
- **Separate stress comparisons:** terminal nominal wealth change, minimum cash and negative-cash flag compared with the last calculated plan; these tests never alter the baseline.
- **Explicit confirmation before destructive actions:** country change and example replacement do not silently reset a plan.
- **Less surprising navigation:** simulation results render after a calculation without forced page restart; file actions on the main page; numeric fields instead of pointer-only sliders for key horizons and stress parameters.
- **Expanded audit:** source-backed UX review, risk catalogue and mathematical unit tests. **This is a review candidate, not an independently peer-reviewed final release.**


- **Straightforward workflow:** inputs, output, inverse goal and comparisons appear in reading order on one page; no calculation settings hidden behind tabs or an Advanced switch.
- **Editable life events always visible:** explicit duration, up-front and monthly costs, income change, and their approximate cumulative net impact.
- **Visible update status:** changing inputs marks the previous results as outdated, prevents stale inverse calculations and distinguishes export of the last calculated scenario from unsaved edits.
- **Socioeconomic risk map:** 87 candidate factors and actual model maturity documented; unimplemented risks never masquerade as calibrated forecasts.
- **Review methodology:** synthetic socioeconomic scenarios and independent user/expert test protocol, clearly distinguished from real external reviews (not performed).
- **GitHub Actions run manually only** to avoid unsolicited workflow-run notifications from repository pushes. Configure GitHub notification preferences separately if unwanted mail persists.


- **France/Vietnam statistical reference explorer**: dated official observations with exact population, average/median, source, and explicit incompatibility with personal inputs.
- **Consent-based optional inflation preset**: preview the World Bank historical observation and choose whether to use it as a non-predictive future assumption. Personal inputs and life events remain unchanged.
- **Global execution plan** with phase dependencies, acceptance criteria and remaining limitations.


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

**Historical population statistics are not personal estimates. No median or per-capita average is silently copied into a financial plan.**

## Online demonstration

The public application is available at **https://financial-adviser.streamlit.app/**. Streamlit Community Cloud may put idle apps to sleep; follow its wake-up prompt if necessary. This hosted application executes on a remote server: use **synthetic data** when trying the demo, and do not enter sensitive personal finances or medical details. For post-publication browser smoke checks (synthetic French projection and Vietnamese mobile display) and their limits, see [Documentation/16_VERIFICATION_APPLICATION_PUBLIQUE.md](Documentation/16_VERIFICATION_APPLICATION_PUBLIQUE.md).

## Run locally

**Release status:** v0.7.0 is a household life-cycle modelling candidate, not a certified final application. Independent human user tests, actuarial/fiscal peer reviews, and physical-device verification remain necessary. See [Review plan](Documentation/18_PROTOCOL_EVALUATIONS_HUMAINES.md). 


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
- [Human-centred software UX reference](Documentation/14_REFERENTIEL_ERGONOMIE.md)
- [Prioritized usability audit](Documentation/15_AUDIT_ERGONOMIQUE_V04.md)
- [Live application verification protocol](Documentation/16_VERIFICATION_APPLICATION_PUBLIQUE.md)

Technical documentation remains primarily in French; interface controls, messages, charts and navigation are localized consistently in French, English or Vietnamese.

## License

No project license has been selected yet. The source is visible on GitHub, but it is **not automatically licensed for redistribution** until a license is added. The reference applications cited in the docs have their own independent licenses; this project does not copy their source code.

## Project plan and official statistical sources

- [Comprehensive execution plan](Documentation/12_PLAN_GLOBAL.md)
- [Statistical data sources, compatibility and user consent](Documentation/13_REFERENCES_STATISTIQUES_V04.md)

### Suggested GitHub About fields

- **Description:** `Transparent financial planning simulator for France & Vietnam — Python/Streamlit, scenarios, life events and Monte Carlo.`
- **Website:** https://financial-adviser.streamlit.app/

These text suggestions are documented here because repository About metadata must be updated using GitHub repository settings, which are separate from Markdown files.

## Socioeconomic model coverage and UX reviews

- [87-factor catalogue with implementation status](Documentation/17_FACTEURS_FINANCIERS_SOCIAUX_ET_RISQUES.md)
- [Independent user and professional-review protocol](Documentation/18_PROTOCOL_EVALUATIONS_HUMAINES.md)
- [Heuristic audit of the v0.5 UX candidate](Documentation/19_REVUE_HEURISTIQUE_MULTIPROFILS.md)

The two GitHub Actions workflows are **manual** (`workflow_dispatch`) to avoid automatic run notifications. They can be launched from the Actions tab when validation is explicitly desired. Changing repository workflows does not directly alter your GitHub account's [email notification settings](https://github.com/settings/notifications).

- [v0.6 design, risk templates and prioritized audit](Documentation/20_REDESIGN_V06.md)

**Validation caveat:** the new scenario module has passed focused local unit tests, but the complete v0.6 Streamlit app has not been browser-tested against this commit. GitHub Actions remain manual to avoid automatic notification emails. No independent human or expert review is claimed.

## Household life-cycle model

[Read the source-backed design and limitations](Documentation/21_CYCLE_VIE_BUDGET_FAMILIAL.md). Child costs change with age (living expenses and childcare/education) and can continue after the 18th birthday to an explicitly configured end age. Adult budgets model hypothetical age-phase adjustments and retirement. Neither the example child costs nor retirement income replacement rates are official estimates. Check whether expenses are **already included** in your household base budget to avoid counting them twice.

The focused local test suite currently covers household cost ages, support stops, pension transitions, JSON compatibility, Monte Carlo and inverse-planning invariants. Full Streamlit browser/device tests and independent expert review are **not** claimed for this candidate.
