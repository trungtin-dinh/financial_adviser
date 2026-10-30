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


def _loan_schedule(plan: Plan) -> tuple[np.ndarray, np.ndarray]:
    """Return outstanding balance and monthly payment, including initial month."""
    n = 12 * plan.years
    balances = np.zeros(n + 1)
    payments = np.zeros(n + 1)
    balances[0] = plan.loan_balance
    fixed = loan_payment(plan.loan_balance, plan.loan_apr_pct, plan.loan_years)
    monthly_interest = plan.loan_apr_pct / 1200.0
    for m in range(1, n + 1):
        before = balances[m - 1]
        if before <= 1e-7:
            continue
        interest = before * monthly_interest
        payment = min(fixed, before + interest)
        payments[m] = payment
        balances[m] = max(0.0, before + interest - payment)
    return balances, payments


def _drivers(plan: Plan) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = plan.years * 12
    t = np.arange(n, dtype=float) / 12.0
    income = plan.monthly_income * np.power(1 + plan.income_growth_pct / 100, t)
    spending = plan.monthly_expenses * np.power(1 + plan.expense_growth_pct / 100, t)
    events = np.zeros(n)
    for event in plan.one_offs:
        events[event.month - 1] += event.amount
    child_costs, adult_costs, retirement_income_change = household_adjustments(plan)
    spending += child_costs + adult_costs + dependent_adjustments(plan)
    income += retirement_income_change
    for item in plan.life_events:
        start = item.first_month - 1
        stop = start + item.duration_months
        spending[start:stop] += item.monthly_expense
        income[start:stop] += item.monthly_income_change
        events[start] -= item.upfront_cost
    outstanding, payments = _loan_schedule(plan)
    return income, spending, events, outstanding, payments


def project(plan: Plan) -> pd.DataFrame:
    """Simulate each month; contributions/events occur before monthly interest."""
    plan.validate()
    n = plan.years * 12
    income, expenses, events, loan, payment = _drivers(plan)
    cash = np.empty(n + 1)
    invested = np.empty(n + 1)
    cash[0], invested[0] = plan.initial_cash, plan.initial_investments
    child_costs, adult_costs, retirement_income_change = household_adjustments(plan)
    dependent_costs = dependent_adjustments(plan)
    rc, ri, inflation = (monthly_rate(v) for v in (
        plan.cash_return_pct, plan.investment_return_pct, plan.inflation_pct))
    for m in range(1, n + 1):
        free_cashflow = income[m - 1] - expenses[m - 1] - payment[m] + events[m - 1]
        cash[m] = (cash[m - 1] + free_cashflow - plan.monthly_investment) * (1 + rc)
        invested[m] = (invested[m - 1] + plan.monthly_investment) * (1 + ri)
    periods = np.arange(n + 1)
    factor = (1 + inflation) ** periods
    nominal = cash + invested - loan
    return pd.DataFrame({
        "month": periods,
        "year": plan.start_year + periods / 12.0,
        "cash": cash,
        "investments": invested,
        "loan_balance": loan,
        "net_worth": nominal,
        "net_worth_real": nominal / factor,
        "purchasing_power_factor": factor,
        "income": np.r_[0, income],
        "expenses": np.r_[0, expenses],
        "loan_payment": payment,
        "one_off": np.r_[0, events],
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
    income, expenses, events, loan, payments = _drivers(plan)
    outcomes[0] = cash + invested - loan[0]
    rc = monthly_rate(plan.cash_return_pct)
    mean_return = monthly_rate(plan.investment_return_pct)
    std_return = plan.investment_volatility_pct / 100.0 / sqrt(12.0)
    negative_cash = cash < 0
    for m in range(1, n + 1):
        free_cashflow = income[m - 1] - expenses[m - 1] - payments[m] + events[m - 1]
        cash = (cash + free_cashflow - plan.monthly_investment) * (1 + rc)
        returns = np.maximum(rng.normal(mean_return, std_return, size=n_paths), -0.99)
        invested = (invested + plan.monthly_investment) * (1 + returns)
        negative_cash |= cash < 0
        outcomes[m] = cash + invested - loan[m]
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
