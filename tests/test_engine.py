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
