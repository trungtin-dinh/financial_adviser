"""Upgrade stored Streamlit plans after an application version change.

A browser tab may keep session_state across Streamlit hot-reloads. Older Plan
instances don't have the new household attributes and must be upgraded rather
than interpreted as the current dataclass.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass

from .models import Plan


def normalize_plan(plan: object) -> tuple[Plan, bool]:
    """Return a validated current plan and whether it needed migration.

    The old class may have been reloaded, so even an instance with similar
    fields may no longer be an instance of the current Plan class.
    Unknown fields and invalid plans raise ValueError; callers must not silently
    overwrite a failed migration with illustrative defaults.
    """
    if (isinstance(plan, Plan) and hasattr(plan, "children")
            and hasattr(plan, "adults") and hasattr(plan, "dependents")):
        plan.validate()
        return plan, False
    if is_dataclass(plan) and not isinstance(plan, type):
        source = asdict(plan)
    elif isinstance(plan, dict):
        source = dict(plan)
    else:
        raise ValueError("Stored plan cannot be migrated safely")
    return Plan.from_dict(source), True
