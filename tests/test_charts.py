"""Financial result charts: numeric semantics, filtering and UI regression."""
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from financial_adviser.charts import (
    DEFAULT_WEALTH_SERIES, WEALTH_SERIES, household_figure,
    uncertainty_figure, wealth_figure,
)
from financial_adviser.engine import monte_carlo, project
from financial_adviser.households import child_example
from financial_adviser.models import Plan
from financial_adviser.ui_i18n import t
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lang", ["fr", "en", "vi"])
def test_default_wealth_chart_is_legible_and_optional_lines_are_hidden(lang):
    plan = Plan(years=5)
    result = project(plan)
    chart = wealth_figure(
        result, plan.goal, plan.start_year, plan.currency,
        DEFAULT_WEALTH_SERIES, lambda key: t(lang, key),
    )
    assert len(chart.data) == 2
    assert [line.name for line in chart.data] == [
        t(lang, "net_worth"), t(lang, "net_worth_real"),
    ]
    np.testing.assert_allclose(chart.data[0].y, result.net_worth)
    np.testing.assert_allclose(chart.data[1].y, result.net_worth_real)
    assert all(isinstance(value, str) for value in chart.layout.xaxis.ticktext)
    assert chart.layout.yaxis.title.text == plan.currency
    assert "2026" in chart.data[0].customdata[1]
    assert t(lang, "chart_month") in chart.data[0].customdata[1]


def test_goal_lines_are_consistent_with_nominal_and_real_net_worth():
    plan = Plan(years=20, inflation_pct=3.5, goal=120000)
    df = project(plan)
    chart = wealth_figure(
        df, plan.goal, plan.start_year, plan.currency,
        WEALTH_SERIES, lambda key: t("fr", key),
    )
    assert len(chart.data) == len(WEALTH_SERIES)
    np.testing.assert_allclose(chart.data[5].y, plan.goal)
    np.testing.assert_allclose(
        chart.data[6].y, plan.goal / df.purchasing_power_factor
    )
    assert chart.data[5].name != chart.data[6].name
    assert chart.data[5].line.dash == "dot"
    assert chart.data[6].line.dash == "dot"
    assert chart.data[0].line.color != chart.data[1].line.color


def test_invalid_series_rejected_and_empty_selection_draws_nothing():
    p = Plan(years=1)
    df = project(p)
    fig = wealth_figure(df, p.goal, p.start_year, p.currency, (), lambda k: k)
    assert not fig.data
    with pytest.raises(ValueError, match="Unknown chart series"):
        wealth_figure(df, p.goal, p.start_year, p.currency,
                      ("net_worth", "not_a_metric"), lambda k: k)


def test_household_chart_keeps_signed_monthly_variations():
    p = Plan(years=1)
    df = project(p).copy()
    df.loc[df.month == 1, "child_expenses"] = 100.0
    df.loc[df.month == 2, "child_expenses"] = -50.0
    fig = household_figure(df, p.start_year, p.currency, lambda k: t("fr", k))
    assert len(fig.data) == 1
    assert 100.0 in fig.data[0].y and -50.0 in fig.data[0].y
    assert fig.data[0].name == t("fr", "household_child_delta")
    # Sum is a signed adjustment, not a gross estimate of child support.
    assert df.child_expenses.sum() == pytest.approx(50.0)


def test_monte_carlo_quantiles_remain_a_distinct_view():
    p = Plan(years=1)
    df = project(p)
    mc = monte_carlo(p, n_paths=100, seed=7)
    chart = uncertainty_figure(df, mc, p.start_year, p.currency,
                               lambda k: t("en", k))
    assert len(chart.data) == 3
    np.testing.assert_allclose(chart.data[1].y, mc.p10)
    np.testing.assert_allclose(chart.data[2].y, mc.p50)
    assert chart.data[1].fill == "tonexty"
    assert chart.layout.yaxis.title.text == "EUR"


def test_chart_controls_do_not_modify_saved_projection():
    plan = replace(Plan(years=2),
                   children=(child_example(2000.0),))
    df = project(plan)
    mc = monte_carlo(plan, n_paths=100, seed=4)
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = "fr"
    app.session_state["plan"] = plan
    app.session_state["result"] = {"plan": plan, "df": df, "mc": mc}
    app.session_state["confirmed_inputs"] = True
    app.run()
    assert not app.exception, app.exception
    assert app.segmented_control(key="result_chart_view").value == "wealth"
    assert app.checkbox(key="chart_curve_net_worth").value is True
    assert app.checkbox(key="chart_curve_net_worth_real").value is True
    assert app.checkbox(key="chart_curve_cash").value is False
    app.checkbox(key="chart_curve_cash").set_value(True).run()
    assert not app.exception, app.exception
    assert app.checkbox(key="chart_curve_cash").value is True
    pd.testing.assert_frame_equal(app.session_state["result"]["df"], df)
    app.segmented_control(key="result_chart_view").set_value("household").run()
    assert not app.exception, app.exception
    app.segmented_control(key="result_chart_view").set_value("uncertainty").run()
    assert not app.exception, app.exception
    assert any(t("fr", "chart_mc_cash_note") in str(x.value)
               for x in app.get("caption"))


def test_no_additional_views_without_relevant_information():
    app = AppTest.from_file(str(ROOT / "pages" / "planning.py"),
                            default_timeout=30)
    app.session_state["language_choice"] = "en"
    app.run()
    app.button(key="load_demo").click().run()
    app.button(key="confirm_example").click().run()
    app.button(key="run_projection").click().run()
    assert not app.exception, app.exception
    assert app.segmented_control(key="result_chart_view").value == "wealth"
    assert "household" not in app.segmented_control(key="result_chart_view").options
    assert "uncertainty" not in app.segmented_control(key="result_chart_view").options
