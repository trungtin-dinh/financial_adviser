"""UI-independent deterministic and probabilistic monthly projection engines.

Conventions are documented in Documentation/02_MODELES_MATHEMATIQUES.md.
No legal tax calculation is performed in v0.1.0.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt

import numpy as np
import pandas as pd

from .models import Plan
from .households import household_adjustments, dependent_adjustments, included_current_spending


def monthly_rate(annual_pct: float) -> float:
    """Effective annual rate expressed as percent -> effective monthly rate."""
    return (1.0 + annual_pct / 100.0) ** (1.0 / 12.0) - 1.0


def loan_payment(balance: float, apr_pct: float, years: int) -> float:
    """Monthly fixed annuity; APR is a nominal annual rate divided by 12."""
    if balance <= 0:
        return 0.0
    r = apr_pct / 1200.0
    n = years * 12
    return balance / n if r == 0 else balance * r / (1.0 - (1.0 + r) ** (-n))


def _amortize(principal: float, apr_pct: float, years: int, first_month: int,
              months: int) -> tuple[np.ndarray, np.ndarray]:
    """Balance and instalment arrays (index 0 = initial state) for one loan.

    The balance is ``principal`` at ``first_month``; the first instalment is due
    the month after. The last instalment is capped at balance plus interest.
    """
    balances = np.zeros(months + 1)
    payments = np.zeros(months + 1)
    balances[first_month] = principal
    fixed = loan_payment(principal, apr_pct, years)
    rate = apr_pct / 1200.0
    for m in range(first_month + 1, months + 1):
        before = balances[m - 1]
        if before <= 1e-7:
            continue
        interest = before * rate
        payment = min(fixed, before + interest)
        payments[m] = payment
        balances[m] = max(0.0, before + interest - payment)
    return balances, payments


def _loan_schedule(plan: Plan) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Total outstanding debt and instalments, plus the new mortgage alone.

    The existing loan starts at month 0. A future mortgage is issued at closing
    (month P) with its first instalment in P+1; both schedules stay independent.
    """
    n = 12 * plan.years
    balances, payments = _amortize(plan.loan_balance, plan.loan_apr_pct, plan.loan_years, 0, n)
    purchase = plan.property_purchase
    if purchase is None:
        new_balances, new_payments = np.zeros(n + 1), np.zeros(n + 1)
    else:
        new_balances, new_payments = _amortize(
            purchase.price - purchase.down_payment, purchase.loan_apr_pct,
            purchase.loan_years, purchase.month, n)
    return balances + new_balances, payments + new_payments, new_balances, new_payments


def _property_values(plan: Plan, periods: np.ndarray) -> np.ndarray:
    """Existing assets plus a home purchased only on or after its closing month."""
    factor = 1.0 + monthly_rate(plan.property_growth_pct)
    values = plan.initial_property_value * factor ** periods
    purchase = plan.property_purchase
    if purchase is not None:
        since = periods - purchase.month
        values = values + np.where(since >= 0, purchase.price * factor ** np.maximum(since, 0), 0.0)
    return values


def _drivers(plan: Plan, household: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
             dependents: np.ndarray | None = None) -> tuple[np.ndarray, ...]:
    n = plan.years * 12
    t = np.arange(n, dtype=float) / 12.0
    income = plan.monthly_income * np.power(1 + plan.income_growth_pct / 100, t)
    spending = plan.monthly_expenses * np.power(1 + plan.expense_growth_pct / 100, t)
    events = np.zeros(n)
    for event in plan.one_offs:
        events[event.month - 1] += event.amount
    recurring = np.zeros(n)
    for flow in plan.recurring_flows:
        recurring[flow.start_month - 1:flow.end_month:flow.interval_months] += flow.amount
    child_costs, adult_costs, retirement_income_change = (
        household if household is not None else household_adjustments(plan))
    spending += child_costs + adult_costs + (
        dependents if dependents is not None else dependent_adjustments(plan))
    income += retirement_income_change
    for item in plan.life_events:
        start = item.first_month - 1
        stop = start + item.duration_months
        spending[start:stop] += item.monthly_expense
        income[start:stop] += item.monthly_income_change
        events[start] -= item.upfront_cost
    purchase_outflow = np.zeros(n)
    if plan.property_purchase is not None:
        purchase = plan.property_purchase
        # Mortgage funds go directly to the seller, never through household cash.
        purchase_outflow[purchase.month - 1] = -(purchase.down_payment + purchase.fees)
    outstanding, payments, new_loan, new_payment = _loan_schedule(plan)
    return (income, spending, events, recurring, purchase_outflow,
            outstanding, payments, new_loan, new_payment)


def project(plan: Plan) -> pd.DataFrame:
    """Simulate each month; contributions/events occur before monthly interest."""
    plan.validate()
    n = plan.years * 12
    child_costs, adult_costs, retirement_income_change = household_adjustments(plan)
    dependent_costs = dependent_adjustments(plan)
    (income, expenses, events, recurring, purchase_outflow,
     loan, payment, new_loan, new_payment) = _drivers(
        plan, (child_costs, adult_costs, retirement_income_change), dependent_costs)
    cash = np.empty(n + 1)
    invested = np.empty(n + 1)
    cash[0], invested[0] = plan.initial_cash, plan.initial_investments
    rc, ri, inflation = (monthly_rate(v) for v in (
        plan.cash_return_pct, plan.investment_return_pct, plan.inflation_pct))
    for m in range(1, n + 1):
        free_cashflow = (income[m - 1] - expenses[m - 1] - payment[m]
                         + events[m - 1] + recurring[m - 1] + purchase_outflow[m - 1])
        cash[m] = (cash[m - 1] + free_cashflow - plan.monthly_investment) * (1 + rc)
        invested[m] = (invested[m - 1] + plan.monthly_investment) * (1 + ri)
    periods = np.arange(n + 1)
    factor = (1 + inflation) ** periods
    # Assets entered explicitly remain distinct from cash and invested capital.
    # A loan never creates property automatically; appreciation is non-cash.
    property_value = _property_values(plan, periods)
    other_assets = np.full(n + 1, plan.initial_other_assets, dtype=float)
    illiquid_assets = property_value + other_assets
    nominal = cash + invested + illiquid_assets - loan
    return pd.DataFrame({
        "month": periods,
        "year": plan.start_year + periods / 12.0,
        "cash": cash,
        "investments": invested,
        "property_value": property_value,
        "other_assets": other_assets,
        "illiquid_assets": illiquid_assets,
        "gross_assets": cash + invested + illiquid_assets,
        "loan_balance": loan,
        "new_mortgage_balance": new_loan,
        "new_mortgage_payment": new_payment,
        "net_worth": nominal,
        "net_worth_real": nominal / factor,
        "purchasing_power_factor": factor,
        "income": np.r_[0, income],
        "expenses": np.r_[0, expenses],
        "loan_payment": payment,
        "one_off": np.r_[0, events],
        "recurring_flow": np.r_[0, recurring],
        "property_purchase_cashflow": np.r_[0, purchase_outflow],
        "child_expenses": np.r_[0, child_costs],
        "adult_expenses": np.r_[0, adult_costs],
        "dependent_expenses": np.r_[0, dependent_costs],
        "retirement_income_change": np.r_[0, retirement_income_change],
    })


@dataclass(frozen=True)
class MonteCarloResult:
    months: np.ndarray
    p10: np.ndarray
    p50: np.ndarray
    p90: np.ndarray
    probability_goal: float
    probability_negative_cash: float
    sample_paths: int
    seed: int


def monte_carlo(plan: Plan, n_paths: int = 1000, seed: int = 42) -> MonteCarloResult:
    """IID normal monthly investment returns (clipped at -99%); no correlations/tax.

    Volatility is annualized standard deviation / sqrt(12), an approximation.
    Cash returns and inflation are deterministic. Percentiles are nominal net worth.
    """
    plan.validate()
    if not 100 <= n_paths <= 20000:
        raise ValueError("Monte Carlo paths must be between 100 and 20,000.")
    if seed < 0:
        raise ValueError("Seed must be non-negative.")
    n = plan.years * 12
    rng = np.random.default_rng(seed)
    # Keep memory roughly O(paths) not O(paths * months) except stored net-worth paths.
    cash = np.full(n_paths, plan.initial_cash, dtype=float)
    invested = np.full(n_paths, plan.initial_investments, dtype=float)
    outcomes = np.empty((n + 1, n_paths))
    (income, expenses, events, recurring, purchase_outflow,
     loan, payments, _, _) = _drivers(plan)
    property_values = _property_values(plan, np.arange(n + 1))
    outcomes[0] = cash + invested + property_values[0] + plan.initial_other_assets - loan[0]
    rc = monthly_rate(plan.cash_return_pct)
    mean_return = monthly_rate(plan.investment_return_pct)
    std_return = plan.investment_volatility_pct / 100.0 / sqrt(12.0)
    negative_cash = cash < 0
    for m in range(1, n + 1):
        free_cashflow = (income[m - 1] - expenses[m - 1] - payments[m]
                         + events[m - 1] + recurring[m - 1] + purchase_outflow[m - 1])
        cash = (cash + free_cashflow - plan.monthly_investment) * (1 + rc)
        returns = np.maximum(rng.normal(mean_return, std_return, size=n_paths), -0.99)
        invested = (invested + plan.monthly_investment) * (1 + returns)
        negative_cash |= cash < 0
        outcomes[m] = cash + invested + property_values[m] + plan.initial_other_assets - loan[m]
    q10, q50, q90 = np.quantile(outcomes, [0.1, 0.5, 0.9], axis=1)
    return MonteCarloResult(
        months=np.arange(n + 1), p10=q10, p50=q50, p90=q90,
        probability_goal=float(np.mean(outcomes[-1] >= plan.goal)),
        probability_negative_cash=float(np.mean(negative_cash)),
        sample_paths=n_paths, seed=seed,
    )


@dataclass(frozen=True)
class GoalSolution:
    """A *conditional* way to meet a nominal goal with non-negative cash every month."""
    lever: str
    amount: float
    feasible: bool
    explanation: str
    scenario: Plan | None = None


def solve_goal(plan: Plan, target: float, horizon_years: int | None = None) -> tuple[GoalSolution, ...]:
    """Solve three separate, not cumulative, inverse scenarios.

    Linear sensitivity is exact for this engine: income, baseline spending and
    initial cash enter the state recurrence additively. A scenario only qualifies
    if terminal nominal net worth >= target AND cash is nonnegative at every month.
    The alternatives are not investment advice and ignore all taxes and fees.
    """
    if not np.isfinite(target) or target < 0:
        raise ValueError("Target must be finite and non-negative")
    candidate = replace(plan, goal=float(target),
                        years=plan.years if horizon_years is None else horizon_years)
    candidate.validate()
    base = project(candidate)
    terminal = float(base.net_worth.iloc[-1])
    cash = base.cash.to_numpy(dtype=float)
    shortfall = max(0., target - terminal)

    def required_unit(delta_terminal: float, delta_cash: np.ndarray) -> float | None:
        if delta_terminal <= 0 and shortfall > 1e-8:
            return None
        req = shortfall / delta_terminal if shortfall > 1e-8 else 0.0
        for c, d in zip(cash, delta_cash):
            if c < -1e-8:
                if d <= 0:
                    return None
                req = max(req, -float(c) / float(d))
        return max(0.0, float(req))

    unit = max(1., candidate.monthly_income * 0.05)
    more_income = project(replace(candidate, monthly_income=candidate.monthly_income + unit))
    amount = required_unit((more_income.net_worth.iloc[-1] - terminal) / unit,
                           (more_income.cash.to_numpy() - cash) / unit)
    solutions = []
    if amount is None or not np.isfinite(amount):
        solutions.append(GoalSolution("income", 0., False, "No feasible income adjustment found."))
    else:
        scenario = replace(candidate, monthly_income=candidate.monthly_income + amount * (1 + 1e-10))
        solutions.append(GoalSolution("income", amount, True,
            "Additional net income per starting month; it follows the chosen income growth assumption.", scenario))

    minimum_spending = included_current_spending(candidate)
    maximum_reduction = candidate.monthly_expenses - minimum_spending
    if maximum_reduction > 1e-9:
        spending_floor = project(replace(candidate, monthly_expenses=minimum_spending))
        d_terminal = (float(spending_floor.net_worth.iloc[-1]) - terminal) / maximum_reduction
        d_cash = (spending_floor.cash.to_numpy() - cash) / maximum_reduction
        savings = required_unit(d_terminal, d_cash)
        if savings is not None and savings <= maximum_reduction + 1e-6:
            savings = min(maximum_reduction, savings)
            scenario = replace(candidate, monthly_expenses=max(
                minimum_spending, candidate.monthly_expenses - savings))
            solutions.append(GoalSolution("expenses", savings, True,
                "Starting spending reduction, respecting costs already included in the baseline.", scenario))
        else:
            solutions.append(GoalSolution("expenses", 0., False,
                "Reducing flexible spending to zero still would not satisfy the target and cash constraint."))
    else:
        solutions.append(GoalSolution("expenses", 0., False,
            "No baseline spending can be removed without cutting already-included costs."))

    unit_cash = max(1., candidate.initial_cash * 0.05)
    added_cash = project(replace(candidate, initial_cash=candidate.initial_cash + unit_cash))
    topup = required_unit((float(added_cash.net_worth.iloc[-1]) - terminal) / unit_cash,
                          (added_cash.cash.to_numpy() - cash) / unit_cash)
    if topup is None or not np.isfinite(topup):
        solutions.append(GoalSolution("capital", 0., False, "No finite initial top-up found."))
    else:
        scenario = replace(candidate, initial_cash=candidate.initial_cash + topup * (1 + 1e-10))
        solutions.append(GoalSolution("capital", topup, True,
            "External cash injection at month zero (not a loan or internal transfer).", scenario))
    return tuple(solutions)
