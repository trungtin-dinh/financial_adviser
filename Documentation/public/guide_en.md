# Public guide — Financial Adviser

This guide explains the simulator's purpose, mathematical assumptions and limitations without exposing implementation details. It is educational information, not personal financial advice.

## 1. Purpose and scope

**Financial Adviser** explores how household income, expenses, cash, investments, debt and financial goals might evolve over time. Users can compare assumptions and include optional life events.

It is neither a live banking dashboard nor a reliable forecast of an individual's future. A scenario uses **one currency**; switching between France and Vietnam does not convert values automatically.

## 2. Models and equations

The model projects finances on a monthly basis. Nominal net worth is assets minus the remaining debt:

$$
N_m = C_m + A_m - D_m
$$

where $C_m$ is cash, $A_m$ investments and $D_m$ outstanding debt in month $m$.

Monthly funds available before transfers between cash and investments are:

$$
F_m = Y_m - E_m - L_m + O_m
$$

An effective annual return $R$ has the following equivalent monthly rate:

$$
r_m = (1+R)^{1/12}-1
$$

With assumed annual inflation $\pi$, net worth in starting-date purchasing power is:

$$
N_m^{\mathrm{real}} = \frac{N_m}{(1+\pi)^{m/12}}
$$

Income, expenses, payments and transfers are applied before monthly returns. Transfers between cash and investments are **not income**. Assumed returns, inflation and future cash flows are not predictions.

Simplified Monte Carlo simulations illustrate the possible spread of investment returns under selected assumptions. Their percentiles are **not guaranteed outcomes**.

## 3. Sources and reliability

The application distinguishes **historical observations**, **user-defined future assumptions** and **legal rules**. A national statistic is not automatically a suitable estimate of a particular household's income or expenses.

Relevant primary sources include [Insee](https://www.insee.fr/fr/information/8184146), the [Banque de France](https://www.banque-france.fr/fr), and the [Vietnam National Statistics Office](https://www.nso.gov.vn/en/).

The separate statistical references page provides the source and period of available observations. National tax rules are not applied automatically in projections.

## 4. How the simulator works

The user journey is straightforward: **enter a plan**, **adjust assumptions**, **run the calculation** and **review the results**.

Charts show net worth, cash, investments and remaining debt. Indicators flag potential cash deficits and whether the stated financial goal is reached. Optional comparisons vary assumptions without silently replacing the reference scenario.

Plans may be imported or exported as JSON at the user's request. No bank transactions are fetched automatically.

## 5. Relationship to other financial tools

Budgeting software mainly tracks spending; portfolio trackers describe investments; planning simulators explore **conditional future scenarios**.

Financial Adviser focuses on the third use case. It is not a replacement for tax preparation, regulated financial advice, pension estimation or comprehensive accounting. The capabilities of other products vary by country and version.

## 6. Quality, privacy and limitations

The model does not comprehensively account for taxes, product fees, social benefits, foreign exchange, or unrepresented property assets.

**Negative cash** indicates an unfunded shortfall, not an approved overdraft or automatic asset sale. Favorable results should not be interpreted as proof that a plan is feasible.

No banking connection is required. Data entered into the hosted application are nevertheless processed by its server during the session. Prefer fictional values or a local installation for sensitive personal information.

## 7. Possible future improvements

Potential extensions include more asset and debt categories, richer uncertainty scenarios and improved country-specific references.

Any future taxation, public benefits or pension rules would require up-to-date official evidence and careful handling of exceptions. **These ideas are not currently available features or release commitments.**

## 8. Design principles

The model emphasizes transparent assumptions, an explicit distinction between observations and projections, and a clear separation between edited inputs and calculated results.

Major scenario changes require deliberate user actions. The application does not infer personal medical or social events or assign them probabilities without evidence.

The intention is to help users critically interpret results rather than treat a single output as the truth.

## 9. Life events and usability

A life event may represent a move, income interruption, healthcare spending or a large purchase. It has a starting date, duration, possible upfront cost and optional monthly income or spending changes.

Events are fully editable and are never assigned automatic personal probabilities. Avoid counting expenses twice when they already appear in the baseline budget.

Everyday settings are shown first; more technical assumptions remain available separately.

## 10. Financial, social and risk factors

Income growth, inflation, investment returns, borrowing, family support and professional or health events may change a financial trajectory.

The simulator distinguishes **sensitivity analysis**, **user-chosen stress scenarios** and **simplified probabilistic investment simulations**. None of these provides an individual probability of job loss, illness or other life events.

Economic dependencies and personal circumstances are only partially represented.

## 11. Evaluation and validation

Quality work includes automated checks for mathematical consistency, data integrity, navigation and multilingual presentation.

These checks do not establish an independent review with real participants, economists, tax experts or actuaries. **External validation must not be assumed completed.**

The model's conclusions remain educational and conditional on its assumptions.

## 12. Household life cycle

Profiles for **children**, **adults** and **other dependents** can describe changes in household costs and income over time.

Child-related spending may vary by age and chosen support period. Adult income may change at an assumed retirement date using a **hypothetical pension**; support for other dependents can be entered separately.

The **already included in current expenses** option helps avoid double-counting baseline costs. Suggested default amounts are fictional illustrations, not national averages. A projection horizon shorter than the support period covers only part of the total costs.
