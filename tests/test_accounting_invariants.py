"""P0 accounting identities and conventions across difficult household scenarios.

These are regression tests, not claims that all real-world finances are modeled.
"""
from dataclasses import replace

import numpy as np
import pytest

from financial_adviser.engine import project
from financial_adviser.models import LifeEvent, OneOff, Plan


@pytest.mark.parametrize("plan", [
    Plan(years=1, cash_return_pct=0, investment_return_pct=0,
         inflation_pct=0, loan_balance=0),
    Plan(years=2, loan_balance=12000, loan_apr_pct=0, loan_years=1,
         monthly_investment=0, goal=0),
    Plan(country="VN", currency="VND", years=3, initial_cash=200_000_000,
         initial_investments=100_000_000, monthly_income=50_000_000,
         monthly_expenses=36_000_000, monthly_investment=8_000_000,
         cash_return_pct=3, investment_return_pct=7, inflation_pct=12),
    Plan(years=2, initial_cash=100, monthly_income=0, monthly_expenses=2000,
         one_offs=(OneOff(3, -5000), OneOff(12, 1000)),
         life_events=(LifeEvent("other", "Unplanned repair", 2, 3,
                                monthly_expense=300, upfront_cost=500),)),
])
def test_nominal_and_real_accounting_identities(plan):
    df = project(plan)
    np.testing.assert_allclose(
        (df["cash"] + df["investments"] - df["loan_balance"]).to_numpy(),
        df["net_worth"].to_numpy(), rtol=1e-12, atol=1e-5,
    )
    np.testing.assert_allclose(
        (df["net_worth"] / df["purchasing_power_factor"]).to_numpy(),
        df["net_worth_real"].to_numpy(), rtol=1e-12, atol=1e-5,
    )
    assert df.iloc[0]["cash"] == pytest.approx(plan.initial_cash)
    assert df.iloc[0]["investments"] == pytest.approx(plan.initial_investments)


def test_internal_transfer_does_not_change_net_worth_without_returns():
    base = Plan(
        years=2, initial_cash=15000, initial_investments=5000,
        monthly_income=3000, monthly_expenses=2000,
        monthly_investment=0, cash_return_pct=0,
        investment_return_pct=0, inflation_pct=0, loan_balance=0,
    )
    no_transfer = project(base)
    transfer = project(replace(base, monthly_investment=600))
    np.testing.assert_allclose(
        no_transfer["net_worth"].to_numpy(),
        transfer["net_worth"].to_numpy(), rtol=0, atol=1e-8,
    )
    assert transfer["cash"].iloc[-1] < no_transfer["cash"].iloc[-1]
    assert transfer["investments"].iloc[-1] > no_transfer["investments"].iloc[-1]


def test_zero_interest_loan_reaches_zero_balance():
    plan = Plan(
        years=2, loan_balance=12000, loan_apr_pct=0, loan_years=1,
        monthly_income=3000, monthly_expenses=2000,
    )
    df = project(plan)
    assert df["loan_balance"].iloc[12] == pytest.approx(0, abs=1e-7)
    assert df["loan_balance"].iloc[-1] == pytest.approx(0, abs=1e-7)
    assert df["loan_payment"].iloc[1:13].sum() == pytest.approx(12000)
    assert df["loan_payment"].iloc[13:].sum() == pytest.approx(0)


def test_cashflow_i18n_has_matching_keys_in_all_languages():
    from financial_adviser.ui_i18n import TEXT

    keys = {
        "cashflow_title", "cashflow_intro", "cashflow_year",
        "cashflow_net", "cashflow_min_cash", "cashflow_negative_months",
        "cashflow_period", "cashflow_income", "cashflow_expenses",
        "cashflow_loan", "cashflow_events", "cashflow_transfer",
        "cashflow_flow", "cashflow_cash", "cashflow_note",
    }
    for lang in ("fr", "en", "vi"):
        assert keys.issubset(TEXT[lang])
        assert all(TEXT[lang][key] for key in keys)
