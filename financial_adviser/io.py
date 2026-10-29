"""Scenario import/export with version tags and strict validation."""

import json
from .models import Plan

SCHEMA_VERSION = 1


def dump_plan(plan: Plan) -> str:
    plan.validate()
    return json.dumps({"schema_version": SCHEMA_VERSION, "plan": plan.to_dict(),
                       "notice": "Illustrative financial projection; no tax/legal advice."},
                      indent=2, ensure_ascii=False)


def load_plan(raw: bytes | str) -> Plan:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if len(raw) > 1_000_000:
        raise ValueError("Scenario file is too large")
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported scenario schema")
    return Plan.from_dict(data["plan"])
