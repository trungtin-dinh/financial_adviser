"""Future property purchase: cash/debt/asset conservation and compatibility."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.cashflow import monthly_cashflow_calendar
from financial_adviser.comparisons import build_comparisons, minimum_comparison_years
from financial_adviser.engine import loan_payment, monte_carlo, project, solve_goal
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import Plan, PropertyPurchase
from financial_adviser.session_compat import normalize_plan
from financial_adviser.ui_i18n import t


def baseline(**kwargs):
    return replace(Plan(
        years=3, initial_cash=100000, initial_investments=0,
        monthly_income=0, monthly_expenses=0, monthly_investment=0,
        income_growth_pct=0, expense_growth_pct=0,
        cash_return_pct=0, investment_return_pct=0,
        property_growth_pct=0, inflation_pct=0, goal=0,
        loan_balance=0,
    ), **kwargs)


def purchase(**kwargs):
    return replace(PropertyPurchase(
        month=3, price=120000, down_payment=20000, fees=5000,
        loan_apr_pct=0, loan_years=20,
    ), **kwargs)


def test_loan_financed_closing_has_only_fee_loss_in_net_worth():
    p = baseline(property_purchase=purchase())
    df = project(p)
    assert df.property_value.iloc[2] == pytest.approx(0)
    assert df.loan_balance.iloc[2] == pytest.approx(0)
    assert df.cash.iloc[2] == pytest.approx(100000)
    assert df.property_value.iloc[3] == pytest.approx(120000)
    assert df.cash.iloc[3] == pytest.approx(75000)
    assert df.new_mortgage_balance.iloc[3] == pytest.approx(100000)
    assert df.loan_balance.iloc[3] == pytest.approx(100000)
    assert df.new_mortgage_payment.iloc[3] == pytest.approx(0)
    assert df.loan_payment.iloc[3] == pytest.approx(0)
    assert df.property_purchase_cashflow.iloc[3] == pytest.approx(-25000)
    assert df.one_off.iloc[3] == 0
    assert df.net_worth.iloc[3] == pytest.approx(95000)  # only fees destroy wealth
    assert df.new_mortgage_payment.iloc[4] == pytest.approx(100000 / 240)
    assert df.new_mortgage_balance.iloc[4] == pytest.approx(100000 - 100000 / 240)
    np.testing.assert_allclose(
        df.cash + df.investments + df.property_value + df.other_assets - df.loan_balance,
        df.net_worth,
    )


def test_unfinanced_purchase_neutral_before_fees():
    p = baseline(property_purchase=purchase(price=80000, down_payment=80000, fees=0))
    df = project(p)
    assert df.cash.iloc[3] == pytest.approx(20000)
    assert df.property_value.iloc[3] == pytest.approx(80000)
    assert df.new_mortgage_balance.iloc[3] == 0
    assert df.net_worth.iloc[3] == pytest.approx(100000)


def test_existing_loan_is_independent_from_future_mortgage():
    existing = baseline(loan_balance=12000, loan_apr_pct=0, loan_years=1)
    with_purchase = replace(existing, property_purchase=purchase())
    before = project(existing)
    after = project(with_purchase)
    np.testing.assert_allclose(after.loan_balance - before.loan_balance,
                               after.new_mortgage_balance)
    np.testing.assert_allclose(after.loan_payment - before.loan_payment,
                               after.new_mortgage_payment)
    assert after.loan_payment.iloc[3] == pytest.approx(1000)
    assert after.loan_payment.iloc[4] == pytest.approx(1000 + 100000 / 240)


def test_mortgage_first_payment_next_month_and_eventually_amortizes():
    p = baseline(years=2, property_purchase=purchase(
        month=2, price=12000, down_payment=2000, fees=0,
        loan_years=1, loan_apr_pct=5))
    df = project(p)
    assert df.new_mortgage_balance.iloc[2] == pytest.approx(10000)
    assert df.new_mortgage_payment.iloc[2] == 0
    assert df.new_mortgage_payment.iloc[3] == pytest.approx(loan_payment(10000, 5, 1))
    assert df.new_mortgage_balance.iloc[14] == pytest.approx(0, abs=1e-6)
    assert df.new_mortgage_payment.iloc[15] == 0


def test_future_property_value_starts_at_closing_and_compounds_after():
    p = baseline(initial_property_value=40000, property_growth_pct=5,
                 property_purchase=purchase(month=13, price=100000, down_payment=50000, fees=0))
    df = project(p)
    assert df.property_value.iloc[12] == pytest.approx(42000)
    assert df.property_value.iloc[13] == pytest.approx(40000 * 1.05**(13/12) + 100000)
    assert df.property_value.iloc[25] == pytest.approx(40000 * 1.05**(25/12) + 105000)


def test_cashflow_calendar_tracks_closing_separately():
    p = baseline(property_purchase=purchase())
    df = project(p)
    cal = monthly_cashflow_calendar(p, df)
    item = cal.loc[cal.month == 3].iloc[0]
    assert item.property_purchase_cashflow == -25000
    assert item.one_off == 0
    assert item.net_cashflow_before_returns == -25000
    assert cal.loc[cal.month == 4, "loan_payment"].item() == pytest.approx(100000 / 240)


def test_monte_carlo_zero_volatility_agrees_with_exact_purchase_schedule():
    p = baseline(
        investment_volatility_pct=0, property_growth_pct=3,
        property_purchase=purchase(month=14, loan_apr_pct=4.2))
    result = project(p)
    mc = monte_carlo(p, n_paths=250, seed=51)
    for q in (mc.p10, mc.p50, mc.p90):
        np.testing.assert_allclose(q, result.net_worth, atol=1e-5)


def test_goal_and_comparison_cannot_skip_property_closing():
    p = baseline(property_purchase=purchase(month=25))
    assert minimum_comparison_years(p) == 3
    with pytest.raises(ValueError, match="obligation"):
        build_comparisons(p, 2, 2.0)
    with pytest.raises(ValueError, match="outside projection"):
        solve_goal(p, 0, horizon_years=2)


def test_old_json_omitting_purchase_is_accepted():
    p = baseline()
    raw = json.loads(dump_plan(p))
    raw["plan"].pop("property_purchase")
    loaded = load_plan(json.dumps(raw))
    assert loaded.property_purchase is None
    assert load_plan(dump_plan(baseline(property_purchase=purchase()))).property_purchase == purchase()


@pytest.mark.parametrize("update", [
    {"month": 0}, {"month": 37}, {"month": 1.5}, {"month": True},
    {"price": 0}, {"price": -1}, {"price": float("nan")},
    {"down_payment": -1}, {"down_payment": 120001}, {"fees": -1},
    {"fees": float("inf")}, {"loan_apr_pct": -1}, {"loan_apr_pct": 101},
    {"loan_years": 0}, {"loan_years": 61}, {"loan_years": True},
])
def test_invalid_future_purchase_rejected(update):
    with pytest.raises(ValueError):
        project(baseline(property_purchase=purchase(**update)))


def test_unknown_fields_and_malformed_future_purchase_json_rejected():
    raw = json.loads(dump_plan(baseline()))
    for purchase_value in ({"invalid": True}, [], True):
        raw["plan"]["property_purchase"] = purchase_value
        with pytest.raises((ValueError, TypeError)):
            load_plan(json.dumps(raw))


def test_migrate_old_session_dataclass_without_purchase_attribute():
    from dataclasses import dataclass

    @dataclass
    class OlderPlan:
        country: str = "FR"
        currency: str = "EUR"
        years: int = 3
        monthly_income: float = 1234

    migrated, changed = normalize_plan(OlderPlan())
    assert changed and migrated.property_purchase is None
    assert migrated.monthly_income == 1234


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_editor_strings_exist_in_all_languages(lang):
    keys = (
        "purchase_title", "purchase_intro", "purchase_enable", "purchase_month",
        "purchase_price", "purchase_down", "purchase_fees", "purchase_apr",
        "purchase_years", "purchase_invalid", "purchase_summary",
        "purchase_no_double_count", "purchase_result_title",
        "purchase_result_explain", "purchase_paid", "purchase_financing",
        "purchase_remaining", "purchase_first_repayment",
        "cashflow_property_purchase",
    )
    assert all(t(lang, key, payment="100", mortgage="80") for key in keys)


def test_streamlit_editor_and_existing_purchases_render():
    p = baseline(property_purchase=purchase())
    app = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "pages" / "planning.py"),
        default_timeout=40,
    )
    app.session_state["language_choice"] = "en"
    app.session_state["plan"] = p
    app.session_state["result"] = {"plan": p, "df": project(p), "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert app.checkbox(key="field_purchase_enabled").value is True
    assert app.number_input(key="field_purchase_month").value == 3
    assert app.number_input(key="field_purchase_down").value == 20000
