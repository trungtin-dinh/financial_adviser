"""Reproducible household life-cycle mathematics, no demographic probabilities."""
from dataclasses import replace
import pytest

from financial_adviser.models import Plan
from financial_adviser.households import AdultBudget, ChildBudget, child_example, household_adjustments
from financial_adviser.engine import project, solve_goal, monte_carlo


def base(**kw):
    p = Plan(years=30, monthly_income=3000, monthly_expenses=1000, initial_cash=0,
             initial_investments=0, monthly_investment=0, cash_return_pct=0.,
             investment_return_pct=0., expense_growth_pct=0., income_growth_pct=0.,
             inflation_pct=0., goal=0.)
    return replace(p, **kw)


def test_child_costs_across_ages_and_stop_at_18():
    child=ChildBudget('child', support_until_age=18, living=(100,150,200,300,400),
                      care_education=(20,30,40,50,60))
    costs, adults, income = household_adjustments(base(children=(child,)))
    assert costs[0] == 120
    assert costs[35] == 120
    assert costs[36] == 180
    assert costs[72] == 240
    assert costs[144] == 350
    assert costs[216] == 0
    assert costs[-1] == 0
    assert (adults == 0).all() and (income == 0).all()


def test_child_support_after_adulthood_until_selected_age():
    c=ChildBudget('student', age_years=17, support_until_age=25, living=(0,0,0,10,200))
    costs,*_=household_adjustments(base(children=(c,)))
    assert costs[0] == 10
    assert costs[12] == 200
    assert costs[95] == 200
    assert costs[96] == 0


def test_future_child_not_counted_before_birth_and_ends_after_age_limit():
    child=ChildBudget('future', arrival_month=25, support_until_age=2, living=(200,0,0,0,0))
    costs,*_=household_adjustments(base(children=(child,)))
    assert costs[23] == 0
    assert costs[24] == 200
    assert costs[47] == 200
    assert costs[48] == 0


def test_two_children_add_without_interference():
    a=ChildBudget('A',age_years=1,living=(100,0,0,0,0))
    b=ChildBudget('B',age_years=1,living=(200,0,0,0,0))
    costs,*_=household_adjustments(base(children=(a,b)))
    assert costs[0] == 300
    assert costs[24] == 0


def test_inflation_of_extra_costs_uses_expense_growth_not_retirement_inflation():
    c=ChildBudget('c', living=(100,100,100,100,100))
    p=base(children=(c,), expense_growth_pct=12, inflation_pct=50)
    costs,*_=household_adjustments(p)
    assert costs[12] == pytest.approx(112)


def test_retirement_transition_by_parent_age_and_income_share():
    person=AdultBudget('adult',age_years=63,income_share_pct=50,retirement_age=65, included_in_baseline=False,
        retirement_replacement_pct=60,expenses_by_age=(0,0,80,120),retirement_expense_change=-20)
    p=base(adults=(person,))
    c, extra, delta=household_adjustments(p)
    assert (c == 0).all()
    assert extra[0] == 80
    assert delta[23] == 0
    assert extra[24] == 60
    assert delta[24] == -600  # 50% of 3000 salary replaced at 60%
    assert project(p).income.iloc[25] == 2400


def test_existing_pension_is_not_replaced_again_at_start():
    adult=AdultBudget('a', age_years=65, retirement_age=65,
        income_share_pct=100,retirement_replacement_pct=50,
        retirement_expense_change=-200)
    p=base(adults=(adult,), income_growth_pct=10, inflation_pct=4)
    income=project(p).income
    assert income.iloc[1] == pytest.approx(3000)
    assert income.iloc[13] == pytest.approx(3120)
    assert project(p).adult_expenses.iloc[1] == 0


def test_future_retirement_pension_is_indexed_after_retirement():
    adult=AdultBudget('a', age_years=64, retirement_age=65,
        income_share_pct=100,retirement_replacement_pct=50)
    p=base(adults=(adult,), income_growth_pct=10, inflation_pct=4)
    income=project(p).income
    assert income.iloc[1] == pytest.approx(3000)
    assert income.iloc[13] == pytest.approx(1650)
    assert income.iloc[25] == pytest.approx(1716)


def test_adult_expense_age_transition_without_retirement():
    adult=AdultBudget('a',age_years=39,income_share_pct=0,
        expenses_by_age=(10,20,30,40),retirement_age=100,included_in_baseline=False)
    _,cost,*_=household_adjustments(base(adults=(adult,)))
    assert cost[0] == 10
    assert cost[12] == 20


def test_budget_uses_only_incremental_child_costs():
    c=ChildBudget('c',living=(200,200,200,200,200))
    without=project(base())
    with_child=project(base(children=(c,)))
    assert with_child.net_worth.iloc[12] - without.net_worth.iloc[12] == -2400
    assert with_child.child_expenses.iloc[1] == 200


def test_household_adult_share_sum_must_not_exceed_100():
    a=AdultBudget('a',income_share_pct=70)
    b=AdultBudget('b',income_share_pct=40)
    with pytest.raises(ValueError,match='shares'):
        base(adults=(a,b)).validate()


def test_invalid_support_stop_or_stage_cost_rejected():
    with pytest.raises(ValueError):
        base(children=(ChildBudget('c', age_years=19, support_until_age=18),)).validate()
    with pytest.raises(ValueError):
        base(children=(ChildBudget('c', living=(-1,0,0,0,0)),)).validate()
    with pytest.raises(ValueError):
        base(adults=(AdultBudget('a',retirement_replacement_pct=float('nan')),)).validate()


def test_legacy_json_without_household_fields_preserved():
    p=base()
    doc=p.to_dict()
    doc.pop('children');doc.pop('adults')
    loaded=Plan.from_dict(doc)
    assert loaded.children == () and loaded.adults == ()


def test_roundtrip_of_household_schedules():
    p=base(children=(ChildBudget('child',living=(1,2,3,4,5),age_years=2),),
           adults=(AdultBudget('parent',age_years=40),))
    assert Plan.from_dict(p.to_dict()) == p


def test_nonnegative_default_example_and_no_unproven_country_rates():
    x=child_example(1500,'a')
    assert x.living[0] > 0 and x.care_education[0] > 0
    assert x.living != sorted(x.living,reverse=True)


def test_monte_carlo_and_inverse_goal_compatible_with_households():
    child=ChildBudget('child',living=(50,50,50,50,50))
    p=base(years=2,children=(child,), initial_cash=15000, initial_investments=100,
           goal=40000, investment_volatility_pct=0)
    a=project(p)
    mc=monte_carlo(p,n_paths=100,seed=42)
    assert mc.p50[-1] == pytest.approx(a.net_worth.iloc[-1])
    sols=solve_goal(p, target=100000)
    assert any(s.feasible for s in sols)


def test_existing_child_already_in_baseline_only_stage_difference_counts():
    c=ChildBudget('c', age_years=2, included_in_baseline=True, support_until_age=18,
                  living=(100,150,200,350,400))
    amounts,*_=household_adjustments(base(children=(c,)))
    assert amounts[0] == 0
    assert amounts[12] == 50
    assert amounts[48] == 100
    assert amounts[216] == -100  # current expense was already in baseline; support ends


def test_future_child_cannot_claim_cost_is_already_in_baseline():
    with pytest.raises(ValueError):
        base(children=(ChildBudget('c', arrival_month=13, included_in_baseline=True),)).validate()


def test_adult_age_stage_baseline_diff_can_be_negative():
    a=AdultBudget('a', age_years=59, income_share_pct=0, retirement_age=100,
                  expenses_by_age=(0,300,100,250),included_in_baseline=True)
    _,cost,_=household_adjustments(base(adults=(a,)))
    assert cost[0] == 0
    assert cost[12] == -200


def test_included_current_foyer_costs_cannot_exceed_total_expenses():
    p=base(monthly_expenses=100, children=(ChildBudget('c', age_years=2,
        living=(200,0,0,0,0), included_in_baseline=True),))
    with pytest.raises(ValueError, match="exceed baseline"):
        p.validate()


def test_goal_seek_never_cuts_below_already_included_child_cost():
    c=ChildBudget('c', age_years=1, living=(400,500,500,500,500), included_in_baseline=True)
    p=base(years=2, monthly_expenses=500, initial_cash=2000, monthly_income=0,
           children=(c,), goal=100000)
    proposals=solve_goal(p,100000)
    option=next(v for v in proposals if v.lever == 'expenses')
    assert not option.feasible or option.scenario.monthly_expenses >= 400


def test_goal_seek_can_reduce_only_unassigned_spending():
    c=ChildBudget('c', age_years=1, living=(400,500,500,500,500), included_in_baseline=True)
    p=base(years=2, monthly_expenses=1000, initial_cash=5000, monthly_income=2000,
           children=(c,), goal=30000)
    solutions=solve_goal(p,30000)
    option=next(v for v in solutions if v.lever=='expenses')
    if option.feasible:
        assert option.amount <= 600 + 1e-6
        assert option.scenario.monthly_expenses >= 400


def test_dependent_costs_are_monthly_and_bounded():
    from financial_adviser.households import DependentBudget, dependent_adjustments
    d = DependentBudget("older parent", first_month=13, duration_months=24,
                        monthly_support=100, monthly_care=50)
    p = base(years=4, dependents=(d,))
    costs = dependent_adjustments(p)
    assert costs[11] == 0
    assert costs[12] == 150
    assert costs[35] == 150
    assert costs[36] == 0
    assert project(p).dependent_expenses.iloc[13] == 150


def test_existing_dependent_in_baseline_releases_budget_after_end():
    from financial_adviser.households import DependentBudget, dependent_adjustments
    d = DependentBudget("family", duration_months=12, monthly_support=100,
                        monthly_care=50, included_in_baseline=True)
    p = base(years=2, dependents=(d,))
    costs = dependent_adjustments(p)
    assert costs[0] == 0
    assert costs[11] == 0
    assert costs[12] == -150


def test_dependent_baseline_budget_cannot_exceed_initial_spending():
    from financial_adviser.households import DependentBudget
    with pytest.raises(ValueError, match="Already included"):
        base(monthly_expenses=50, dependents=(
            DependentBudget("family", monthly_care=100, included_in_baseline=True),)).validate()


def test_dependent_json_roundtrip_and_legacy_scenario():
    from financial_adviser.households import DependentBudget
    p = base(years=2, dependents=(DependentBudget("aunt", duration_months=18, monthly_support=250),))
    assert type(Plan.from_dict(p.to_dict()).dependents[0]).__name__ == "DependentBudget"
    old = p.to_dict()
    del old["dependents"]
    assert Plan.from_dict(old).dependents == ()


def test_dependent_validation_rejects_future_in_baseline_and_outside_horizon():
    from financial_adviser.households import DependentBudget
    with pytest.raises(ValueError):
        base(years=2, dependents=(DependentBudget(
            "family", first_month=2, duration_months=12, included_in_baseline=True),)).validate()
    with pytest.raises(ValueError):
        base(years=2, dependents=(DependentBudget(
            "family", duration_months=48),)).validate()


def test_dependent_costs_included_in_monte_carlo_and_goal_seek():
    from financial_adviser.households import DependentBudget
    d = DependentBudget("partner", duration_months=24, monthly_support=75)
    p = base(years=2, dependents=(d,), initial_cash=10000,
             initial_investments=1000, investment_volatility_pct=0)
    assert monte_carlo(p, n_paths=100).p50[-1] == pytest.approx(project(p).net_worth.iloc[-1])
    assert solve_goal(p, 100000)
