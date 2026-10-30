"""The templates are hypothetical, non-destructive and fully editable."""
from dataclasses import replace

import pytest

from financial_adviser.models import Plan
from financial_adviser.engine import project
from financial_adviser.scenarios import PRESET_IDS, proposed_event, stress_impact


def base(**kwargs):
    return replace(Plan(), years=5, start_year=2026,
                   cash_return_pct=0, investment_return_pct=0,
                   monthly_income=3000, monthly_expenses=2000,
                   initial_cash=10000, initial_investments=0,
                   monthly_investment=0, loan_balance=0, **kwargs)


@pytest.mark.parametrize('key', PRESET_IDS)
def test_generated_event_is_valid_and_does_not_mutate_plan(key):
    original = base()
    event = proposed_event(original, key, 13)
    assert original.life_events == ()
    assert event.first_month == 13
    assert 0 <= event.monthly_expense
    assert event.upfront_cost >= 0
    replace(original, life_events=(event,)).validate()
    outcome = stress_impact(original, key, 13)
    assert outcome.event == event
    assert outcome.terminal_delta <= 1e-7
    assert original.life_events == ()


def test_stress_shock_is_not_a_probability():
    impact = stress_impact(base(), 'job_gap')
    assert impact.event.duration_months == 3
    assert impact.event.monthly_income_change == -3000
    assert impact.terminal_delta == pytest.approx(-9000)
    assert not hasattr(impact, 'probability')


def test_generated_event_clips_default_at_end_but_rejects_explicit_overrun():
    p = base()
    assert proposed_event(p, 'child_care', 59).duration_months == 2
    with pytest.raises(ValueError):
        proposed_event(p, 'child_care', 59, duration_months=36)
    with pytest.raises(ValueError):
        proposed_event(p, 'job_gap', first_month=61)
    with pytest.raises(ValueError):
        proposed_event(p, 'not_a_scenario')


def test_stress_maintains_existing_events_and_investment_transfer():
    p = base()
    extra = proposed_event(p, 'family_support', 1)
    p = replace(p, life_events=(extra,), monthly_investment=200)
    first = project(p)
    result = stress_impact(p, 'unexpected_purchase')
    assert result.terminal_delta == pytest.approx(-4000)
    assert project(p).equals(first)


def test_default_templates_are_proportional_to_selected_plan_currency():
    p = replace(base(), country='VN', currency='VND', monthly_expenses=20_000_000,
                monthly_income=30_000_000)
    event = proposed_event(p, 'health_costs')
    assert event.monthly_expense == 5_000_000
    assert event.monthly_income_change == -9_000_000
    assert event.upfront_cost == 10_000_000
