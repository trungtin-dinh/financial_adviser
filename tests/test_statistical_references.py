"""Contract tests for sourced, consent-based financial reference data."""
from dataclasses import asdict, replace
import json
import pytest
from financial_adviser.models import Plan
from financial_adviser.statistical_references import (ReferencePoint, load_references, can_autofill, confirmed_inflation_update)


def observed(country="FR", value=2.4):
    return {"country":country, "value_pct":value,"observation_year":2025,
            "source_url":"https://api.worldbank.org/v2/country/FRA/indicator/FP.CPI.TOTL.ZG?format=json",
            "indicator":"FP.CPI.TOTL.ZG"}


def test_country_specific_and_units():
    fr=load_references("FR");vn=load_references("VN")
    assert len(fr)>=2 and len(vn)>=2
    assert all(x.country=="FR" and x.currency=="EUR" for x in fr)
    assert all(x.country=="VN" and x.currency=="VND" for x in vn)


def test_no_mismatched_income_or_expense_is_autofilled():
    for c in ("FR","VN"):
        for ref in load_references(c):
            for field in ("monthly_income","monthly_expenses","initial_cash","inflation_pct"):
                assert not can_autofill(ref,field)


def test_no_median_mean_confusion():
    vn=load_references("VN")
    assert all(x.statistic=="mean" for x in vn)
    fr=load_references("FR")
    assert all(x.statistic=="median" for x in fr)


def test_non_official_domain_rejected():
    item=asdict(load_references("FR")[0]);item["source_url"]="https://www.insee.fr.attack.example/"
    with pytest.raises(ValueError): ReferencePoint.from_dict(item)


def test_missing_context_rejected():
    item=asdict(load_references("FR")[0]);item["population"]=""
    with pytest.raises(ValueError): ReferencePoint.from_dict(item)


def test_inflation_requires_explicit_consent():
    p=Plan();old=p.to_dict()
    with pytest.raises(PermissionError):confirmed_inflation_update(p,observed(),False)
    assert p.to_dict()==old


def test_inflation_changes_only_optional_field():
    p=Plan(monthly_income=3222,monthly_expenses=1211,life_events=())
    other=p.to_dict();updated=confirmed_inflation_update(p,observed(value=1.5),True)
    assert updated.inflation_pct == 1.5
    assert updated.monthly_income == 3222 and updated.monthly_expenses == 1211
    for k in other:
        if k!='inflation_pct': assert updated.to_dict()[k] == other[k]


def test_inflation_wrong_country_or_source_rejected():
    for v in [observed(country="VN"),{**observed(),"source_url":"https://example.org"},
              {**observed(),"indicator":"other"},observed(value=999), {**observed(), "country": "FR", "source_url": "https://api.worldbank.org/v2/country/VNM/indicator/FP.CPI.TOTL.ZG"}]:
        with pytest.raises(ValueError): confirmed_inflation_update(Plan(),v,True)


def test_invalid_country_rejected():
    with pytest.raises(ValueError): load_references("US")
