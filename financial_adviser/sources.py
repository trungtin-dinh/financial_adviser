"""Optional public macroeconomic data reader. Observations are NOT forecasts."""

from __future__ import annotations

from datetime import datetime, timezone

import requests

WB_INDICATOR = "FP.CPI.TOTL.ZG"  # Annual CPI inflation, percent (World Bank)
WB_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
WB_DOC = "https://datahelpdesk.worldbank.org/knowledgebase/articles/889392"


def fetch_recent_inflation(country: str, timeout: float = 7.0) -> dict:
    if country not in {"FR", "VN"}:
        raise ValueError("Unsupported country")
    code = {"FR": "FRA", "VN": "VNM"}[country]
    url = WB_URL.format(country=code, indicator=WB_INDICATOR)
    r = requests.get(url, params={"format": "json", "per_page": 80}, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("Unexpected World Bank API response")
    for entry in payload[1]:
        if entry.get("value") is not None:
            value = float(entry["value"])
            if not -100 < value < 1000:
                raise ValueError("Invalid inflation observation")
            return {
                "country": country,
                "value_pct": value,
                "observation_year": int(entry["date"]),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "source_url": r.url,
                "indicator": WB_INDICATOR,
            }
    raise ValueError("No available inflation observations")
