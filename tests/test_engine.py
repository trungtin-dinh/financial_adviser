"""Model invariants and calculation benchmarks (pytest)."""
from dataclasses import replace

import numpy as np
import pytest

from financial_adviser.engine import loan_payment, monte_carlo, monthly_rate, project
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import OneOff, Plan


def plan(**kwargs):
    return replace(Plan(years=1, initial_cash=0, initial_investments=0,
                        monthly_income=0, monthly_expenses=0,
                        monthly_investment=0, cash_return_pct=0,
                        investment_return_pct=0, inflation_pct=0,
                        income_growth_pct=0, expense_growth_pct=0,
                        loan_balance=0), **kwargs)


def test_zero_cashflow_zero_rates():
    df = project(plan())
    assert len(df) == 13
    assert (df.net_worth == 0).all()


def test_monthly_contributions_are_transfers_not_new_income():
    p = plan(monthly_income=100, monthly_investment=100)
    df = project(p)
    assert df.cash.iloc[-1] == pytest.approx(0)
    assert df.investments.iloc[-1] == pytest.approx(1200)
    assert df.net_worth.iloc[-1] == pytest.approx(1200)


def test_cashflow_and_oneoff():
    p = plan(monthly_income=100, monthly_expenses=40,
             one_offs=(OneOff(month=2, amount=-70, description="repair"),))
    df = project(p)
    assert df.net_worth.iloc[-1] == pytest.approx(12 * 60 - 70)
    assert df.one_off.iloc[2] == -70


def test_one_offs_same_month_sum():
    p = plan(one_offs=(OneOff(1, 50), OneOff(1, -20)))
    assert project(p).net_worth.iloc[1] == pytest.approx(30)


def test_effective_rate():
    assert (1 + monthly_rate(12)) ** 12 == pytest.approx(1.12)


def test_inflation_discount():
    p = plan(initial_cash=1000, inflation_pct=12)
    df = project(p)
    assert df.net_worth.iloc[-1] == pytest.approx(1000)
    assert df.net_worth_real.iloc[-1] == pytest.approx(1000 / 1.12)


def test_loan_zero_interest_and_balance():
    p = plan(monthly_income=1000, loan_balance=1200, loan_apr_pct=0, loan_years=1)
    df = project(p)
    assert loan_payment(1200, 0, 1) == pytest.approx(100)
    assert df.loan_balance.iloc[-1] == pytest.approx(0)
    assert df.cash.iloc[-1] == pytest.approx(10800)
    assert df.net_worth.iloc[0] == -1200


def test_loan_positive_interest_amortized():
    p = plan(loan_balance=10000, loan_apr_pct=4, loan_years=1,
             monthly_income=1500)
    df = project(p)
    assert df.loan_balance.iloc[-1] == pytest.approx(0, abs=1e-6)
    assert df.loan_payment.iloc[1] > 10000/12


def test_loans_lasting_beyond_projection():
    p = plan(loan_balance=20000, loan_apr_pct=0, loan_years=5)
    df = project(p)
    assert df.loan_balance.iloc[-1] == pytest.approx(16000)


def test_monte_carlo_reproducible():
    p = plan(monthly_investment=50, monthly_income=100,
             investment_volatility_pct=20)
    a, b = monte_carlo(p, n_paths=250, seed=17), monte_carlo(p, n_paths=250, seed=17)
    assert np.array_equal(a.p50, b.p50)
    assert a.probability_goal == b.probability_goal


def test_monte_carlo_zero_vol_equals_deterministic():
    p = plan(monthly_income=500, monthly_investment=300,
             investment_return_pct=7, investment_volatility_pct=0)
    a, b = monte_carlo(p, n_paths=300), project(p)
    assert a.p10[-1] == pytest.approx(b.net_worth.iloc[-1])
    assert a.p50[-1] == pytest.approx(b.net_worth.iloc[-1])
    assert a.p90[-1] == pytest.approx(b.net_worth.iloc[-1])


def test_cash_shortfall_detection():
    p = plan(monthly_expenses=100, investment_volatility_pct=0)
    assert monte_carlo(p, 250).probability_negative_cash == 1.0


def test_json_roundtrip():
    p = plan(one_offs=(OneOff(month=3, amount=-19.5, description="test"),))
    assert load_plan(dump_plan(p)) == p


def test_json_schema_rejected():
    with pytest.raises(ValueError):
        load_plan('{"schema_version": 222, "plan": {}}')


def test_invalid_plan_rejected():
    with pytest.raises(ValueError):
        project(plan(initial_cash=-1))
    with pytest.raises(ValueError):
        project(plan(one_offs=(OneOff(13, 10),)))
    with pytest.raises(ValueError):
        monte_carlo(plan(), n_paths=2)


def test_life_event_recurring_cost_income_and_upfront():
    from financial_adviser.models import LifeEvent
    event = LifeEvent("Health / Care", "Temporary expense", 3, 2,
                      monthly_expense=25, monthly_income_change=-10, upfront_cost=100)
    baseline = project(plan(monthly_income=100))
    alternative = project(plan(monthly_income=100, life_events=(event,)))
    assert alternative.net_worth.iloc[2] == baseline.net_worth.iloc[2]
    assert alternative.net_worth.iloc[3] == pytest.approx(baseline.net_worth.iloc[3] - 135)
    assert alternative.net_worth.iloc[4] == pytest.approx(baseline.net_worth.iloc[4] - 170)
    assert alternative.net_worth.iloc[12] == pytest.approx(baseline.net_worth.iloc[12] - 170)


def test_life_event_validation_and_json_roundtrip():
    from financial_adviser.models import LifeEvent
    from financial_adviser.io import dump_plan, load_plan
    event = LifeEvent("Child / Dependent", "Childcare", 2, 3, monthly_expense=200)
    p = plan(life_events=(event,))
    assert load_plan(dump_plan(p)) == p
    with pytest.raises(ValueError):
        project(plan(life_events=(replace(event, duration_months=12),)))
    with pytest.raises(ValueError):
        project(plan(life_events=(replace(event, upfront_cost=-100),)))
    with pytest.raises(ValueError):
        project(plan(life_events=(replace(event, first_month=0),)))


def test_old_json_scenario_loads_without_life_events():
    import json
    from financial_adviser.io import load_plan
    data = plan().to_dict()
    del data["life_events"]
    restored = load_plan(json.dumps({"schema_version": 1, "plan": data}))
    assert restored.life_events == ()


def test_inverse_goal_solutions_meet_target_and_cash():
    from financial_adviser.engine import solve_goal
    p = plan(monthly_income=250, monthly_expenses=200, initial_cash=100)
    options = solve_goal(p, 1000)
    assert {option.lever for option in options} == {"income", "expenses", "capital"}
    for opt in options:
        if opt.feasible:
            d = project(opt.scenario)
            assert d.net_worth.iloc[-1] >= 1000 - 1e-4
            assert d.cash.min() >= -1e-4


def test_goal_unreachable_by_spending_reduction():
    from financial_adviser.engine import solve_goal
    p = plan(monthly_income=0, monthly_expenses=0)
    options = {x.lever: x for x in solve_goal(p, 1000)}
    assert not options["expenses"].feasible
    assert options["income"].feasible
    assert options["capital"].feasible


def test_inverse_repair_negative_cash_even_when_goal_reached():
    from financial_adviser.engine import solve_goal
    p = plan(initial_cash=0, initial_investments=10000, monthly_expenses=100)
    baseline = project(p)
    assert baseline.net_worth.iloc[-1] > 100
    assert baseline.cash.min() < 0
    options = solve_goal(p, 100)
    for opt in options:
        if opt.feasible:
            assert project(opt.scenario).cash.min() >= -1e-4


def test_inverse_goal_with_life_event():
    from financial_adviser.engine import solve_goal
    from financial_adviser.models import LifeEvent
    p = plan(initial_cash=200, life_events=(LifeEvent("Large purchase", "New car", 6, 1,
                            upfront_cost=5000),))
    options = solve_goal(p, 1000)
    assert any(opt.feasible for opt in options)
    for opt in options:
        if opt.feasible:
            d = project(opt.scenario)
            assert d.net_worth.iloc[-1] >= 1000 - 1e-4
            assert d.cash.min() >= -1e-4
