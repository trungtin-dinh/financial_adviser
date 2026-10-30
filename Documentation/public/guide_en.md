# Public guide — Financial Adviser

This guide explains the simulator's purpose, assumptions, worked examples and limits. It is educational information, not personal financial advice.

## 1. Purpose and scope

**Financial Adviser** explores how household income, expenses, cash, investments, debt and financial goals might evolve over time. Users can compare assumptions and include optional life events.

It is neither a live banking dashboard nor a reliable forecast of an individual's future. A scenario uses **one currency**; switching between France and Vietnam does not convert values automatically.

### What can a projection answer?

The simulator addresses **conditional** questions: “If my household keeps these income, spending and saving assumptions, how might net worth evolve over ten years?”, “What changes if I support a relative?”, or “Can I reach a target without exhausting available cash?”. It does not identify the best investment or make decisions for you.

**Before starting**, collect consistent estimates of household **net monthly income**, ordinary spending **excluding any loan repayment entered separately**, available cash, existing investments and outstanding loan principal. Approximate, defensible amounts are better than falsely precise ones. Entirely fictional figures are fine.

Two households can have identical net worth but very different **liquidity**. Investments are not automatically sold to pay an unexpected bill. That is why the guide distinguishes **net worth**, **cash** and **monthly cash flows**.

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

### The order of monthly operations

At the beginning of each projected month, income is added to cash, while spending, loan payments and applicable event costs are deducted. One-off inflows are added. The planned transfer to investments then leaves cash and enters invested capital. Assumed monthly returns are applied afterward.

With a monthly transfer $T$ and monthly rates $r_C$ and $r_A$, the balances follow $C_m=(C_{m-1}+F_m-T)(1+r_C)$ and $A_m=(A_{m-1}+T)(1+r_A)$. Moving €400 from cash to investments does **not** create €400 of new wealth: it only changes its location.

**Entirely hypothetical example**, with no returns or events: €3,000 income, €2,000 ordinary expenses and a €300 loan payment leave €700 before investment transfers. Transferring €400 to investments leaves an additional €300 in cash and €400 in investments; the loan principal also declines by the principal portion of the payment.

Baseline income and spending change according to the selected annual growth assumptions. Annual effective returns and inflation are converted into equivalent monthly rates. **The loan's nominal annual rate** is instead divided by twelve to calculate monthly interest. The loan follows scheduled fixed payments until repaid.

### Nominal wealth, purchasing power and targets

**Nominal** net worth is expressed in currency units at the date shown. **Real** net worth expresses that amount in the purchasing power of the starting date. For illustration, €100,000 in ten years with hypothetical annual inflation of 2% would have a starting-date purchasing power of about €82,035. This is not an inflation forecast.

The entered financial target is **nominal**. Reaching it at the end does not necessarily mean cash remained positive in every month. Review both measures.

### Reverse planning: what would be needed to reach a target?

The goal-planning feature estimates three **independent levers**: **extra starting monthly net income**, a **reduction in baseline monthly expenses**, or an **external initial cash contribution**. For each lever separately, the resulting plan must reach the final nominal target **while keeping cash non-negative in every month**. The three adjustments are not combined automatically.

The spending reduction cannot erase family costs you have already explicitly included in baseline expenses. Initial extra cash means **new money from outside the existing household assets**, not a transfer between accounts. An unavailable lever means no qualifying solution was identified **under the current assumptions and constraints**, not that the real-life target is universally impossible.

## 3. Sources and reliability

The application distinguishes **historical observations**, **user-defined future assumptions** and **legal rules**. A national statistic is not automatically a suitable estimate of a particular household's income or expenses.

Relevant primary sources include [Insee](https://www.insee.fr/fr/information/8184146), the [Banque de France](https://www.banque-france.fr/fr), and the [Vietnam National Statistics Office](https://www.nso.gov.vn/en/).

The separate statistical references page provides the source and period of available observations. National tax rules are not applied automatically in projections.

### Assessing a public statistic

Always check the **producer**, **publication date**, **reference period**, **population**, **units** and **indicator definition**. The median income of one person is not the net income of an entire household. A general inflation index may not describe your personal spending basket.

**France and Vietnam** have different statistical systems and social protection arrangements. A national average is not directly transferable between countries or to an individual. Your scenario inputs remain your own: public references provide context, not guarantees.

Keep a future return, pension or wage-growth figure clearly labelled as a **scenario assumption**, even if it happens to resemble a historical statistic. The “Sources and rules” page helps distinguish descriptive observations from rules that are not included in the projection.

## 4. How the simulator works

The user journey is straightforward: **enter a plan**, **adjust assumptions**, **run the calculation** and **review the results**.

Charts show net worth, cash, investments and remaining debt. Indicators flag potential cash deficits and whether the stated financial goal is reached. Optional comparisons use a **shared, user-selected horizon** without silently replacing the reference scenario. Life-event dates can be shown or hidden on the main chart to provide temporal context.

Plans may be imported or exported as JSON at the user's request. No bank transactions are fetched automatically.

### Recommended workflow

1. **Describe your current position:** household net income, recurring expenses, accessible cash, investments, any outstanding loan and the projection horizon.
2. **Check baseline spending:** do not count separately entered loan instalments or transfers to investments a second time as ordinary spending.
3. **Describe changes you know or want to explore:** household members, support for relatives, hypothetical retirement and time-limited events.
4. **Review advanced assumptions:** income and spending growth, inflation, returns and volatility. Adjust illustrative values instead of treating them as defaults valid for everybody.
5. **Run the projection**, then inspect the minimum cash balance, debt evolution and purchasing-power-adjusted net worth before focusing on the target.
6. **Change one assumption at a time** to understand its effect; then consider separate stress scenarios.

### Reading indicators correctly

**Net worth** adds cash and invested assets and subtracts outstanding principal. The **cash buffer** compares initial cash with current spending plus the modelled loan payment: it is a static indicator, not a safety guarantee. The **loan-payment / net-income ratio** is not a statutory bank debt-service test. A net-worth increase may coexist with a declining cash balance.

After editing inputs, displayed results may still belong to the **last completed projection**. Run it again before drawing conclusions. Exporting a scenario preserves assumptions; it is neither a bank statement nor evidence of future performance.

## 5. Relationship to other financial tools

Budgeting software mainly tracks spending; portfolio trackers describe investments; planning simulators explore **conditional future scenarios**.

Financial Adviser focuses on the third use case. It is not a replacement for tax preparation, regulated financial advice, pension estimation or comprehensive accounting. The capabilities of other products vary by country and version.

### Selecting the right use case

| Question | What this simulator can show | What it cannot replace |
|---|---|---|
| What if monthly costs rise? | Side-by-side conditional projections | Detailed expense and invoice tracking |
| How might a move or income gap affect me? | Dated events with costs and income changes | Supplier quotes or benefit eligibility |
| Can I reach a wealth target? | Nominal target comparisons and cash constraints | Personal regulated investment advice |
| What if someone retires? | A **hypothetical** pension and income transition | Official pension entitlement statements |
| What if markets perform worse? | Investment sensitivity and simulated dispersion | Reliable market forecasts or full risk modelling |

Scenario comparisons measure **sensitivity** to assumptions; they do not establish which future will occur.

## 6. Quality, privacy and limitations

The model does not comprehensively account for taxes, product fees, social benefits, foreign exchange, or unrepresented property assets.

**Negative cash** indicates an unfunded shortfall, not an approved overdraft or automatic asset sale. The optional **Resilience** section distinguishes static reserve coverage in months of current spending from a hypothetical one-time expense on a selected date. It compares cash before and after that expense and estimates the largest expense that keeps projected cash nonnegative through the full horizon. This capacity is zero if the baseline already contains a deficit. Income, investments and other plan inputs remain unchanged; the figure is neither a recommended buffer nor a financing guarantee. Favorable results should not be interpreted as proof that a plan is feasible.

No banking connection is required. Data entered into the hosted application are nevertheless processed by its server during the session. Prefer fictional values or a local installation for sensitive personal information.

### Questions to ask of any result

- **Liquidity:** does cash ever fall below zero, even briefly? Investments are not automatically liquidated to cover the shortfall.
- **Consistency:** are loan payments, family costs and events each counted once?
- **Purchasing power:** is a nominal target still meaningful after inflation?
- **Fragility:** does the outcome depend on unusually strong investment returns or income growth?
- **Completeness:** are important taxes, insurance premiums, fees, property, assets or recurring obligations missing?

The model uses simplified returns and does not capture all charges, taxes or product-specific schedules. Entering a mortgage does **not** automatically add the corresponding property to assets. A homeowner's total actual wealth may therefore differ substantially from the displayed total.

**Privacy:** avoid personally identifying details and precise sensitive values in the hosted version when unnecessary. Not connecting a bank account does not mean entries never reach the hosting service.

## 7. Possible future improvements

Potential extensions include more asset and debt categories, richer uncertainty scenarios and improved country-specific references.

Any future taxation, public benefits or pension rules would require up-to-date official evidence and careful handling of exceptions. **These ideas are not currently available features or release commitments.**

### Understanding missing capabilities

Comprehensive individual taxes, social benefits, valued property, several investment asset classes, multiple currencies and legally determined pensions require additional data and assumptions. An omitted item does **not** imply its real-life value is zero.

For some situations you can manually represent a known impact as a **one-off amount** or a **change in monthly income or spending**. Only do so when you know the estimate and can clearly distinguish it from an official calculation. Planned additions should never be interpreted as features already available.

## 8. Design principles

The model emphasizes transparent assumptions, an explicit distinction between observations and projections, and a clear separation between edited inputs and calculated results.

Major scenario changes require deliberate user actions. The application does not infer personal medical or social events or assign them probabilities without evidence.

The intention is to help users critically interpret results rather than treat a single output as the truth.

### Assumptions remain under your control

The baseline scenario is explicit: suggestions do not alter your position without an action. Loading a ready-made example may replace existing inputs after confirmation; event templates only enter a plan when you choose them. An **illustrative value** is not an **observed statistic**.

For meaningful comparisons, keep a reference scenario and build variants with **one changed assumption** at a time: horizon, returns, expenses, children, household income or retirement date. If many parameters change together, their individual contributions are difficult to identify.

The number of decimal places displayed is not the precision of any economic prediction. Results are calculated for **your chosen assumptions**, not for a known future.

## 9. Life events and usability

A life event may represent a move, income interruption, healthcare spending or a large purchase. It has a starting date, duration, possible upfront cost and optional monthly income or spending changes.

Events are fully editable and are never assigned automatic personal probabilities. Avoid counting expenses twice when they already appear in the baseline budget.

Everyday settings are shown first; more technical assumptions remain available separately.

### One-off versus recurring events

A one-off cash flow is applied only in its selected month, such as a €2,000 purchase in month 12. A **life-event entry** can combine an upfront cost, extra monthly spending and a monthly income change over a defined interval.

**Fictional example:** a move begins in month 7, lasts two months, costs €1,500 upfront and adds €200 a month in expenses. Its direct effect is €1,900 before returns and inflation. If the new rent is already included in baseline expenses, do not enter that €200 again.

An income loss is a **negative income change**; additional expenses and upfront costs are positive. The start month is included in the duration, and the whole event must fit inside the projection horizon.

Suggested situations—an employment gap, healthcare costs, major purchase, childcare, family support or relocation—are **editable fictional examples** scaled to the scenario. They are not national estimates, personal probabilities or automatically expected events.

## 10. Financial, social and risk factors

Income growth, inflation, investment returns, borrowing, family support and professional or health events may change a financial trajectory.

The simulator distinguishes **sensitivity analysis**, **user-chosen stress scenarios** and **simplified probabilistic investment simulations**. None of these provides an individual probability of job loss, illness or other life events.

Economic dependencies and personal circumstances are only partially represented.

### Three different ways to explore uncertainty

**Sensitivity:** compare the central investment-return assumption with a lower and a higher one. A two-percentage-point change could mean testing 5% against 3% and 7% annually. These cases have no assigned likelihood.

**Stress tests:** apply **one selected shock at a time** (temporary lost income, unexpected expense, help for a relative…) to the baseline. Examine both the change in final net worth **and** the lowest cash balance. These tests are not combined with each other or silently added to the current scenario. Set a start month and compare the baseline and stress cash trajectories, the first deficit month, the duration of negative cash and the scenario's greatest funding gap. Shock costs are illustrative amounts derived from the entered budget. An already-negative baseline is identified separately. **A simulated shortfall does not imply access to overdraft or credit.**

**Monte Carlo:** monthly investment returns vary randomly around a selected average with an assumed volatility. **P10, P50 and P90** describe the **simulated nominal-net-worth distribution** at each date. For example, P10 is the amount below which 10% of simulated trajectories fall at that date. These are not guarantees or individual forecasts.

Simulated monthly returns are assumed independent and follow a simplified distribution capped at a monthly loss near 99%. Income, spending, debt, cash returns and inflation remain deterministic. **Important:** the fraction of runs with negative cash may therefore be 0% or 100%; it is not an empirically calibrated liquidity-crisis probability.

The simulator does not assign personal probabilities to illness, job loss, accidents or family events.

## 11. Evaluation and validation

Quality work includes automated checks for mathematical consistency, data integrity, navigation and multilingual presentation.

These checks do not establish an independent review with real participants, economists, tax experts or actuaries. **External validation must not be assumed completed.**

The model's conclusions remain educational and conditional on its assumptions.

### What checks mean—and what they cannot establish

Consistency checks can detect invalid values, irregular repayment schedules, internal transfer errors and display problems. Such checks reduce obvious mistakes but **cannot confirm that your assumptions are realistic or that a forecast will come true**.

A full assessment would also require feedback from actual users, documented real-world cases and independent expert reviews of the financial models and national rules. Such external validation is **not claimed**.

If a result looks surprising, first revisit the currency, starting year, horizon, costs already included in baseline spending, event dates and the last scenario actually calculated.

## 12. Household life cycle

Profiles for **children**, **adults** and **other dependents** can describe changes in household costs and income over time.

Child-related spending may vary by age and chosen support period. Adult income may change at an assumed retirement date using a **hypothetical pension**; support for other dependents can be entered separately.

The **already included in current expenses** option helps avoid double-counting baseline costs. Suggested default amounts are fictional illustrations, not national averages. A projection horizon shorter than the support period covers only part of the total costs.

### Children: separate expense categories

For each child, distinguish **living expenses** from **care or education** expenses across five age brackets: **0–2, 3–5, 6–11, 12–17 and 18–29 years**. Set the initial age, arrival date and chosen end of support (up to age 30). These are modelling categories, **not** official cost brackets.

**Fictional example:** an existing child accounts for €350 of a household's €2,000 current monthly expenses. If the next age bracket is estimated at €450, the additional cost is the **€100 difference** (before any assumed spending growth), not a further €450 on top of €2,000. For a future child, costs begin on the chosen date and cannot already be included in today's spending.

### Adults and hypothetical retirement

You may allocate up to **100% of net household income** to described adults. Each adult has an age, income share, chosen retirement age, **hypothetical** pension replacement ratio and spending across four age brackets: 18–39, 40–59, 60–74 and 75+. Someone already retired is assumed to be receiving their current pension: the replacement factor is **not** applied twice. A simulated pension subsequently changes with assumed inflation, not official pension regulations.

### Other dependents and safeguards

Support for a parent or other relative can include monthly financial assistance and care-related costs with a starting month and duration. When support is already included in baseline expenses, flag it so that only **changes** are considered; ending the support period can then reduce those baseline costs.

Check that all already-included amounts remain compatible with the stated total spending. The model does not infer social benefits, medical costs from age or a date of death. If the horizon ends before the end of support, cumulative figures cover **only the simulated period**. Suggested costs are fictional.

