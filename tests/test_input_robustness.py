"""Malformed scenarios are refused cleanly instead of crashing later."""
import json

import numpy as np
import pytest

from financial_adviser.engine import project
from financial_adviser.io import dump_plan, format_oneoffs, load_plan, parse_oneoffs
from financial_adviser.models import MAX_ABS_AMOUNT, OneOff, Plan


def _load(plan_fields: dict) -> Plan:
    raw = Plan().to_dict()
    raw.update(plan_fields)
    return load_plan(json.dumps({"schema_version": 1, "plan": raw}))


@pytest.mark.parametrize("fields", [
    {"years": 2.5},                       # accepted before, then crashed the engine
    {"start_year": 2026.0},
    {"loan_years": True},
    {"monthly_income": "3000"},
    {"monthly_income": MAX_ABS_AMOUNT * 10},  # produced NaN results before
    {"monthly_expenses": 1e308},
    {"life_events": [{"category": 3, "label": "x", "first_month": 1, "duration_months": 1}]},
    {"life_events": [{"category": "health", "label": None, "first_month": 1, "duration_months": 1}]},
    {"life_events": ["not an object"]},
    {"one_offs": [{"month": 1, "amount": 1.0}] * 101},
    {"one_offs": [{"month": 1, "amount": 1.0, "description": "x" * 121}]},
    {"one_offs": ["1,2"]},
    {"recurring_flows": [{"start_month": 1, "end_month": 2, "interval_months": 1, "amount": 1e300}]},
    {"children": [{"label": "A", "living": [1e300, 0, 0, 0, 0]}]},
    {"adults": [{"label": "A", "included_in_baseline": "yes"}]},
    {"property_purchase": {"month": 1, "price": 1e300, "down_payment": 0.0, "fees": 0.0,
                           "loan_apr_pct": 3.0, "loan_years": 20}},
])
def test_malformed_import_raises_value_error(fields):
    with pytest.raises(ValueError):
        _load(fields)


def test_large_but_allowed_vnd_amounts_stay_finite_over_sixty_years():
    plan = Plan(country="VN", currency="VND", years=60, initial_cash=MAX_ABS_AMOUNT,
                initial_investments=MAX_ABS_AMOUNT, monthly_income=MAX_ABS_AMOUNT,
                monthly_investment=MAX_ABS_AMOUNT, investment_return_pct=200.0,
                income_growth_pct=200.0, goal=MAX_ABS_AMOUNT)
    frame = project(plan)
    assert np.isfinite(frame.select_dtypes("number").to_numpy()).all()


def test_integral_amounts_written_as_json_integers_still_load():
    plan = _load({"monthly_income": 3000, "initial_cash": 0})
    assert plan.monthly_income == 3000


def test_one_off_descriptions_with_commas_and_quotes_round_trip():
    items = (OneOff(3, -1500.0, 'Voiture, occasion "citadine"'), OneOff(14, 800.0, ""),
             OneOff(20, 10.5, "Prime\nannuelle"))
    text = format_oneoffs(items)
    assert parse_oneoffs(text, years=2) == items
    plan = Plan(years=2, one_offs=items)
    assert load_plan(dump_plan(plan)).one_offs == items


def test_legacy_one_off_text_with_trailing_comma_is_still_read():
    assert parse_oneoffs("3,-100.0,\n5,20,Cadeau", years=1) == (
        OneOff(3, -100.0, ""), OneOff(5, 20.0, "Cadeau"))
