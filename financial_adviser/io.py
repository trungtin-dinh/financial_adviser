"""Scenario import/export with version tags and strict validation."""

import csv
from io import StringIO
import json

from .models import OneOff, Plan

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


def format_oneoffs(items: tuple[OneOff, ...]) -> str:
    """CSV text for the one-off editor; quotes descriptions containing commas."""
    out = StringIO()
    writer = csv.writer(out, lineterminator="\n")
    for item in items:
        writer.writerow((item.month, item.amount, item.description) if item.description
                        else (item.month, item.amount))
    return out.getvalue().rstrip("\n")


def parse_oneoffs(raw: str, years: int) -> tuple[OneOff, ...]:
    if not raw.strip():
        return ()
    lines = list(csv.reader(StringIO(raw), skipinitialspace=True))
    if len(lines) > 100:
        raise ValueError("too many events")
    parsed = []
    for row in lines:
        if not row or not any(s.strip() for s in row):
            continue
        if len(row) not in (2, 3):
            raise ValueError("invalid event row")
        parsed.append(OneOff(int(row[0].strip()), float(row[1].strip()),
                             row[2].strip() if len(row) == 3 else ""))
    if any(not 1 <= item.month <= years * 12 for item in parsed):
        raise ValueError("invalid event month")
    return tuple(parsed)
