"""Versioned official reference observations, never silently mapped into personal data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import math
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_FILE = Path(__file__).resolve().parents[1] / "data" / "statistical_references.json"
COUNTRIES = {"FR": "EUR", "VN": "VND"}
SOURCE_HOSTS = {"www.insee.fr", "www.nso.gov.vn"}
STATS = {"median", "mean", "percentile", "observed_rate"}


@dataclass(frozen=True)
class ReferencePoint:
    id: str
    country: str
    metric: str
    statistic: str
    value: float
    currency: str
    period: str
    observed_year: int
    published_on: str
    precision: str
    population: str
    source_name: str
    source_url: str
    mapping: str
    mapping_reason: str

    @classmethod
    def from_dict(cls, payload: dict) -> "ReferencePoint":
        if not isinstance(payload, dict) or set(payload) != set(cls.__dataclass_fields__):
            raise ValueError("Invalid reference fields")
        p = cls(**payload)
        if p.country not in COUNTRIES or p.currency != COUNTRIES[p.country]:
            raise ValueError("Country/currency mismatch")
        if p.statistic not in STATS or p.mapping not in {"not_directly_compatible", "exactly_compatible"}:
            raise ValueError("Invalid statistic or mapping")
        if not isinstance(p.observed_year, int) or not 2000 <= p.observed_year <= date.today().year:
            raise ValueError("Invalid reference year")
        date.fromisoformat(p.published_on + "-01" if len(p.published_on) == 7 else p.published_on)
        if not isinstance(p.value, (int, float)) or not math.isfinite(p.value) or p.value < 0:
            raise ValueError("Invalid reference value")
        if p.period != "month" or not p.id.strip() or not p.population.strip() or not p.mapping_reason.strip():
            raise ValueError("Insufficient contextualization")
        address = urlparse(p.source_url)
        if address.scheme != "https" or address.hostname not in SOURCE_HOSTS or address.username:
            raise ValueError("Non-official source URL")
        return p


def load_references(country: str, path: Path | None = None) -> tuple[ReferencePoint, ...]:
    if country not in COUNTRIES:
        raise ValueError("Unsupported country")
    raw = json.loads((path or DEFAULT_FILE).read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1 or not isinstance(raw.get("observations"), list):
        raise ValueError("Unsupported statistical reference catalogue")
    date.fromisoformat(raw["snapshot_checked_on"])
    all_points = [ReferencePoint.from_dict(x) for x in raw["observations"]]
    ids = [x.id for x in all_points]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate reference id")
    return tuple(x for x in all_points if x.country == country)


def can_autofill(ref: ReferencePoint, field: str) -> bool:
    """Fail closed: currently none of the surveyed demographics match a plan field."""
    return bool(ref.mapping == "exactly_compatible" and ref.metric == field)


def confirmed_inflation_update(plan, observation: dict, consent: bool):
    """Update an optional hypothesis after explicit consent, without touching private inputs.

    This takes an observed inflation rate; it is deliberately NOT called a forecast.
    The consumer must show publication year, source and disclaimer before calling.
    """
    from dataclasses import replace
    if not consent:
        raise PermissionError("Explicit confirmation is required")
    if not isinstance(observation, dict) or observation.get("country") != plan.country:
        raise ValueError("Inflation observation country mismatch")
    url = urlparse(str(observation.get("source_url", "")))
    if url.scheme != "https" or url.hostname != "api.worldbank.org":
        raise ValueError("Expected the official World Bank API")
    if observation.get("indicator") != "FP.CPI.TOTL.ZG":
        raise ValueError("Incorrect inflation indicator")
    expected_country = {"FR": "FRA", "VN": "VNM"}[plan.country]
    expected_path = f"/v2/country/{expected_country}/indicator/FP.CPI.TOTL.ZG"
    if url.path.rstrip("/") != expected_path:
        raise ValueError("Inflation API country or path mismatch")
    if not isinstance(observation.get("observation_year"), int) or not 2000 <= observation["observation_year"] <= date.today().year:
        raise ValueError("Invalid observation period")
    try:
        value = float(observation["value_pct"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("Invalid inflation data") from exc
    if not math.isfinite(value) or not -99 < value <= 200:
        raise ValueError("Invalid inflation assumption")
    updated = replace(plan, inflation_pct=value)
    updated.validate()
    return updated
