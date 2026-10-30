"""Ensure existing live Streamlit tabs survive v0.6 -> v0.7 schema changes."""
from dataclasses import dataclass, asdict
import pytest
from financial_adviser.models import Plan
from financial_adviser.session_compat import normalize_plan


@dataclass
class PreHouseholdPlan:
    country: str = 'FR'
    currency: str = 'EUR'
    years: int = 20
    monthly_income: float = 3300.
    monthly_expenses: float = 2200.
    goal: float = 60000.


def test_current_plan_untouched():
    p = Plan()
    actual, changed = normalize_plan(p)
    assert actual is p and not changed


def test_old_dataclass_migrated_preserving_earnings_and_spending():
    old = PreHouseholdPlan()
    actual, changed = normalize_plan(old)
    assert changed and actual.monthly_income == 3300.
    assert actual.monthly_expenses == 2200.
    assert actual.children == () and actual.adults == ()
    assert actual.goal == 60000.


def test_dict_old_plan_migrates():
    actual, changed = normalize_plan({'country': 'VN', 'currency': 'VND', 'years': 8})
    assert changed and actual.currency == 'VND' and actual.children == ()


def test_do_not_destroy_bad_saved_plan():
    with pytest.raises(ValueError):
        normalize_plan({'unknown': 'data'})
    with pytest.raises(ValueError):
        normalize_plan(object())
