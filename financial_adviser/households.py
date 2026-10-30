"""Optional, incremental household life-cycle cash flows.

No demographic probability or nationally representative cost estimate is inferred.
Users specify incremental spending in the scenario's currency and income shares.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .models import Plan

# Inclusive first age, exclusive last age. These bands are *model conventions*,
# not empirical thresholds: real expenses need not increase monotonically.
CHILD_AGE_BANDS = ((0, 3), (3, 6), (6, 12), (12, 18), (18, 30))
ADULT_AGE_BANDS = ((18, 40), (40, 60), (60, 75), (75, 181))


@dataclass(frozen=True)
class ChildBudget:
    """Incremental nominal monthly amounts at scenario start, by child's age.

    arrival_month: 1 for a child already in household, or chosen future arrival.
    age_years: integer years old at arrival_month (usually zero for a birth).
    support_until_age: exclusive age when the costs stop, editable 1..30.
    Values are IN ADDITION to baseline household monthly_expenses. The user must
    exclude these costs from baseline to avoid double counting.
    """
    label: str
    age_years: int = 0
    arrival_month: int = 1
    support_until_age: int = 25
    living: tuple[float, ...] = (0., 0., 0., 0., 0.)
    care_education: tuple[float, ...] = (0., 0., 0., 0., 0.)
    included_in_baseline: bool = False


@dataclass(frozen=True)
class AdultBudget:
    """Optional adult ageing and retirement, not a pension or health model.

    income_share_pct is the percentage of the starting total *net household*
    monthly income from this adult. The sum across adults cannot exceed 100%.
    retirement_replacement_pct replaces this adult's net salary share with a
    synthetic net pension at the chosen retirement age, not a legal entitlement.
    Future pension grows with inflation after transition, instead of wages.
    expenses_by_age are incremental costs beyond baseline ordinary expenses.
    """
    label: str
    age_years: int = 40
    income_share_pct: float = 100.0
    retirement_age: int = 65
    retirement_replacement_pct: float = 60.0
    expenses_by_age: tuple[float, ...] = (0., 0., 0., 0.)
    retirement_expense_change: float = 0.0
    included_in_baseline: bool = True


@dataclass(frozen=True)
class DependentBudget:
    """Extra support for an adult relative or another non-child dependent.

    These are *user-specified* cash costs, not diagnosed healthcare needs,
    eligibility estimates or a probability of dependency. An existing expense
    may be included in the household baseline and is then subtracted after
    the end of support.
    """
    label: str
    relation: str = "parent"
    first_month: int = 1
    duration_months: int = 120
    monthly_support: float = 0.0
    monthly_care: float = 0.0
    included_in_baseline: bool = False


DEPENDENT_RELATIONS = ("parent", "adult_relative", "partner", "other")


def _amounts(values: tuple[float, ...], length: int, key: str) -> None:
    if not isinstance(values, (tuple, list)) or len(values) != length:
        raise ValueError(f"{key} must contain exactly {length} stage values")
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 for value in values):
        raise ValueError(f"{key} must contain finite nonnegative amounts")


def validate_household(plan: "Plan") -> None:
    if len(plan.children) > 12 or len(plan.adults) > 8 or len(plan.dependents) > 12:
        raise ValueError("Too many household members")
    for child in plan.children:
        if not isinstance(child, ChildBudget):
            raise ValueError("Invalid child budget")
        if not 1 <= len(child.label.strip()) <= 100:
            raise ValueError("Child needs a name or label")
        if not isinstance(child.age_years, int) or not 0 <= child.age_years <= 29:
            raise ValueError("Child age must be 0–29")
        if not isinstance(child.arrival_month, int) or not 1 <= child.arrival_month <= plan.years * 12:
            raise ValueError("Child arrival month outside projection")
        if not isinstance(child.support_until_age, int) or not child.age_years < child.support_until_age <= 30:
            raise ValueError("Child support must end after starting age, by 30")
        if not isinstance(child.included_in_baseline, bool) or (child.included_in_baseline and child.arrival_month != 1):
            raise ValueError("Only a child already present can have costs included in baseline")
        _amounts(child.living, 5, "child living expenses")
        _amounts(child.care_education, 5, "child care and education expenses")
    for person in plan.dependents:
        if not isinstance(person, DependentBudget):
            raise ValueError("Invalid non-child dependent")
        if not 1 <= len(person.label.strip()) <= 100:
            raise ValueError("Dependent requires a short name")
        if person.relation not in DEPENDENT_RELATIONS:
            raise ValueError("Unknown dependent relation")
        if (not isinstance(person.first_month, int) or not isinstance(person.duration_months, int)
                or person.first_month < 1 or person.duration_months < 1
                or person.first_month + person.duration_months - 1 > plan.years * 12):
            raise ValueError("Dependent support must fit within projection horizon")
        if not isinstance(person.included_in_baseline, bool) or (
                person.included_in_baseline and person.first_month != 1):
            raise ValueError("Future dependent expenses cannot be in the current budget")
        for amount in (person.monthly_support, person.monthly_care):
            if not isinstance(amount, (float, int)) or not math.isfinite(amount) or amount < 0:
                raise ValueError("Dependent monthly costs must be finite and nonnegative")
    shares = 0.0
    for adult in plan.adults:
        if not isinstance(adult, AdultBudget):
            raise ValueError("Invalid adult budget")
        if not 1 <= len(adult.label.strip()) <= 100:
            raise ValueError("Adult needs a name or label")
        if not isinstance(adult.age_years, int) or not 18 <= adult.age_years <= 120:
            raise ValueError("Adult age must be 18–120")
        if not isinstance(adult.retirement_age, int) or not 18 <= adult.retirement_age <= 100:
            raise ValueError("Retirement age must be 18–100")
        for amount, key, upper in ((adult.income_share_pct, "income share", 100.),
                                   (adult.retirement_replacement_pct, "income replacement", 200.)):
            if not isinstance(amount, (float, int)) or not math.isfinite(amount) or not 0 <= amount <= upper:
                raise ValueError(f"Invalid {key}")
        if not isinstance(adult.retirement_expense_change, (float, int)) or not math.isfinite(adult.retirement_expense_change):
            raise ValueError("Invalid retirement expense change")
        if not isinstance(adult.included_in_baseline, bool):
            raise ValueError("Invalid adult baseline scope")
        _amounts(adult.expenses_by_age, 4, "adult expenses")
        shares += adult.income_share_pct
    if shares > 100.0000001:
        raise ValueError("Combined adults' income shares cannot exceed 100%")
    if included_current_spending(plan) > plan.monthly_expenses + 1e-7:
        raise ValueError("Already included household items exceed baseline spending")


def included_current_spending(plan: "Plan") -> float:
    """Lower bound on ordinary spending implied by already-included components."""
    return float(sum(
        c.living[_stage(c.age_years, CHILD_AGE_BANDS)] +
        c.care_education[_stage(c.age_years, CHILD_AGE_BANDS)]
        for c in plan.children if c.included_in_baseline
    ) + sum(a.expenses_by_age[_stage(a.age_years, ADULT_AGE_BANDS)]
            for a in plan.adults if a.included_in_baseline)
      + sum(d.monthly_support + d.monthly_care for d in plan.dependents
            if d.included_in_baseline))


def child_example(baseline_monthly_expenses: float, label: str = "Child") -> ChildBudget:
    """Synthetic demo only: NOT official statistics or a recommended family budget."""
    base = max(0., baseline_monthly_expenses)
    return ChildBudget(label=label, living=tuple(round(base * x, 2) for x in (.10, .12, .14, .19, .20)),
                       care_education=tuple(round(base * x, 2) for x in (.12, .10, .08, .08, .13)))


def _stage(age: int, bands: tuple[tuple[int, int], ...]) -> int:
    for index, (start, end) in enumerate(bands):
        if start <= age < end:
            return index
    raise ValueError("Age outside model bands")


def household_adjustments(plan: "Plan") -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return child spending, adult spending and difference to baseline income.

    All arrays are for projected months 1..N. Child/adult age advances once every
    12 months from start/arrival (birthday month otherwise unknown). Extra costs
    are indexed with *expense_growth_pct*; they are not automatically tied to
    CPI. Negative retirement expense changes are allowed.
    """
    validate_household(plan)
    n = 12 * plan.years
    child_spending = np.zeros(n, dtype=float)
    adult_spending = np.zeros(n, dtype=float)
    income_delta = np.zeros(n, dtype=float)
    idx = np.arange(n)
    expense_factor = np.power(1. + plan.expense_growth_pct / 100., idx / 12.)
    income_factor = np.power(1. + plan.income_growth_pct / 100., idx / 12.)
    for child in plan.children:
        if child.included_in_baseline:
            initial_band = _stage(child.age_years, CHILD_AGE_BANDS)
            baseline_child = child.living[initial_band] + child.care_education[initial_band]
            child_spending -= baseline_child * expense_factor
        for month in range(child.arrival_month, n + 1):
            age = child.age_years + (month - child.arrival_month) // 12
            if age >= child.support_until_age:
                break
            band = _stage(age, CHILD_AGE_BANDS)
            child_spending[month - 1] += (child.living[band] + child.care_education[band]) * expense_factor[month - 1]
    for adult in plan.adults:
        if adult.included_in_baseline:
            initial_band = _stage(adult.age_years, ADULT_AGE_BANDS)
            adult_spending -= adult.expenses_by_age[initial_band] * expense_factor
        share = adult.income_share_pct / 100.
        annual_age = adult.age_years + idx // 12
        for band, (start, end) in enumerate(ADULT_AGE_BANDS):
            mask = (annual_age >= start) & (annual_age < end)
            adult_spending[mask] += adult.expenses_by_age[band] * expense_factor[mask]
        retirement_start_index = max(0, (adult.retirement_age - adult.age_years) * 12)
        if retirement_start_index >= n:
            continue
        mask = idx >= retirement_start_index
        # If the person is already retired at t=0, the input household income
        # already includes the actual current pension. Do NOT replace it again
        # or add a retirement-specific expense transition a second time.
        if adult.age_years >= adult.retirement_age:
            pension = plan.monthly_income * share * np.power(
                1. + plan.inflation_pct / 100., idx[mask] / 12.)
        else:
            adult_spending[mask] += adult.retirement_expense_change * expense_factor[mask]
            # Future pension: illustrative replacement of last net working pay,
            # indexed thereafter with inflation (not wage growth).
            salary_at_retirement = (plan.monthly_income * share *
                (1. + plan.income_growth_pct / 100.) ** (retirement_start_index / 12.))
            months_retired = idx[mask] - retirement_start_index
            pension = salary_at_retirement * adult.retirement_replacement_pct / 100. * np.power(
                1. + plan.inflation_pct / 100., months_retired / 12.)
        income_delta[mask] += pension - plan.monthly_income * share * income_factor[mask]
    return child_spending, adult_spending, income_delta


def dependent_adjustments(plan: "Plan") -> np.ndarray:
    """Monthly additional support for other dependents, relative to base costs.

    Returns signed cash-expense differences, which may become negative after
    an existing dependency ends. All values use the scenario currency.
    """
    count = plan.years * 12
    factor = np.power(1. + plan.expense_growth_pct / 100.,
                      np.arange(count, dtype=float) / 12.)
    delta = np.zeros(count, dtype=float)
    for person in plan.dependents:
        monthly = person.monthly_support + person.monthly_care
        if person.included_in_baseline:
            delta -= monthly * factor
        start = person.first_month - 1
        end = start + person.duration_months
        delta[start:end] += monthly * factor[start:end]
    return delta
