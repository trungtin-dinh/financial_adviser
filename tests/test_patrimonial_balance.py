"""Financial balance-sheet regression tests for explicitly entered illiquid assets."""
from dataclasses import replace
import json

import numpy as np
import pytest

from financial_adviser.charts import wealth_figure
from financial_adviser.custom_comparison import compare_custom_scenarios, make_custom_variant
from financial_adviser.engine import monte_carlo, project
from financial_adviser.io import dump_plan, load_plan
from financial_adviser.models import Plan
from financial_adviser.ui_i18n import t


def example(**changes):
    return replace(Plan(
        years=2, initial_cash=12000, initial_investments=8000,
        monthly_income=3000, monthly_expenses=2000, monthly_investment=400,
        income_growth_pct=0, expense_growth_pct=0,
        cash_return_pct=0, investment_return_pct=0, inflation_pct=0,
        loan_balance=0, goal=0,
    ), **changes)


def test_legacy_zero_assets_keep_existing_results_and_stock_identity():
    a = example()
    df = project(a)
    assert (df.property_value == 0).all()
    assert (df.other_assets == 0).all()
    np.testing.assert_allclose(df.cash + df.investments - df.loan_balance, df.net_worth)
    np.testing.assert_allclose(df.cash + df.investments, df.gross_assets)


def test_home_is_explicit_and_mortgage_does_not_create_property_value():
    a = example(loan_balance=100000, loan_apr_pct=0, loan_years=20)
    no_home = project(a)
    assert (no_home.property_value == 0).all()
    b = replace(a, initial_property_value=160000, initial_other_assets=15000)
    with_home = project(b)
    np.testing.assert_allclose(no_home.cash, with_home.cash)
    np.testing.assert_allclose(no_home.investments, with_home.investments)
    np.testing.assert_allclose(no_home.loan_balance, with_home.loan_balance)
    np.testing.assert_allclose(with_home.net_worth - no_home.net_worth, 175000)
    np.testing.assert_allclose(
        with_home.cash + with_home.investments
        + with_home.property_value + with_home.other_assets
        - with_home.loan_balance,
        with_home.net_worth,
    )


def test_property_appreciation_is_nominal_not_spendable_cash():
    a = example(initial_property_value=100000, property_growth_pct=5.0)
    b = replace(a, property_growth_pct=0)
    new, old = project(a), project(b)
    assert new.property_value.iloc[12] == pytest.approx(105000)
    assert new.property_value.iloc[24] == pytest.approx(110250)
    np.testing.assert_allclose(new.cash, old.cash)
    np.testing.assert_allclose(new.investments, old.investments)
    np.testing.assert_allclose(new.net_worth - old.net_worth,
                               new.property_value - old.property_value)


def test_monte_carlo_zero_volatility_agrees_with_property_value():
    a = example(initial_property_value=100000,
                initial_other_assets=3000, property_growth_pct=3,
                investment_volatility_pct=0, investment_return_pct=5)
    df = project(a)
    mc = monte_carlo(a, n_paths=250, seed=19)
    assert mc.p10[-1] == pytest.approx(df.net_worth.iloc[-1])
    assert mc.p50[-1] == pytest.approx(df.net_worth.iloc[-1])
    assert mc.p90[-1] == pytest.approx(df.net_worth.iloc[-1])


def test_old_json_still_imports_with_zero_illiquid_assets():
    payload = json.loads(dump_plan(example()))
    for key in ("initial_property_value", "initial_other_assets", "property_growth_pct"):
        payload["plan"].pop(key)
    loaded = load_plan(json.dumps(payload))
    assert loaded.initial_property_value == 0
    assert loaded.initial_other_assets == 0
    assert loaded.property_growth_pct == 0


@pytest.mark.parametrize("updates", [
    {"initial_property_value": -1},
    {"initial_other_assets": -100},
    {"property_growth_pct": -100},
    {"property_growth_pct": 201},
    {"property_growth_pct": float("nan")},
])
def test_invalid_property_assumptions_rejected(updates):
    with pytest.raises(ValueError):
        project(example(**updates))


def test_custom_comparison_supports_property_and_preserves_reference():
    a = example(initial_property_value=100000)
    b = make_custom_variant(a, {
        "initial_property_value": 120000, "property_growth_pct": 0,
    })
    assert a.initial_property_value == 100000
    diff = compare_custom_scenarios(a, b, years=a.years)
    assert diff.nominal_difference == pytest.approx(20000)


@pytest.mark.parametrize("language", ("fr", "en", "vi"))
def test_property_series_and_translations(language):
    a = example(initial_property_value=100000, initial_other_assets=5000)
    df = project(a)
    names = ("patrimony_title", "patrimony_property", "patrimony_other",
             "patrimony_growth", "patrimony_no_cash", "patrimony_breakdown",
             "patrimony_gross_assets", "patrimony_result_note",
             "custom_field_initial_property_value",
             "custom_field_initial_other_assets", "custom_field_property_growth_pct")
    assert all(t(language, name) for name in names)
    fig = wealth_figure(df, a.goal, a.start_year, a.currency,
                        ("property_value", "other_assets"), lambda k: t(language, k))
    assert len(fig.data) == 2
    np.testing.assert_allclose(fig.data[0].y, df.property_value)
    np.testing.assert_allclose(fig.data[1].y, df.other_assets)


def test_planner_renders_assets_from_saved_scenario():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest

    a = example(initial_property_value=150000, initial_other_assets=3000)
    page = Path(__file__).resolve().parents[1] / "pages" / "planning.py"
    app = AppTest.from_file(str(page), default_timeout=40)
    app.session_state["language_choice"] = "fr"
    app.session_state["plan"] = a
    app.session_state["result"] = {"plan": a, "df": project(a), "mc": None}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert app.number_input(key="field_property_value").value == 150000
    assert app.number_input(key="field_other_assets").value == 3000
