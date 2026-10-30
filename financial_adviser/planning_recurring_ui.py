"""Localized editor for user-specified, explicitly dated periodic cash flows."""
from __future__ import annotations

from math import isfinite

import pandas as pd
import streamlit as st

from financial_adviser.models import Plan, RecurringFlow

PERIODS = {"monthly": 1, "quarterly": 3, "yearly": 12}


def parse_recurring_rows(rows: list[dict]) -> tuple[RecurringFlow, ...]:
    """Strictly parse editable table rows, without truncating fractional months."""
    if len(rows) > 100:
        raise ValueError("At most 100 recurring entries")
    result = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid recurring row")
        try:
            start = row["start_month"]
            end = row["end_month"]
            amount = row["amount"]
            frequency = row["frequency"]
            label = row.get("description", "")
            if (isinstance(start, bool) or isinstance(end, bool)
                    or not isfinite(float(start)) or not isfinite(float(end))
                    or int(start) != float(start) or int(end) != float(end)):
                raise ValueError("Months must be whole numbers")
            if frequency not in PERIODS:
                raise ValueError("Unsupported recurring frequency")
            if isinstance(amount, bool) or not isfinite(float(amount)):
                raise ValueError("Recurring amount must be finite")
            if not isinstance(label, str) or len(label) > 120:
                raise ValueError("Invalid recurring description")
            result.append(RecurringFlow(
                start_month=int(start), end_month=int(end),
                interval_months=PERIODS[frequency],
                amount=float(amount), description=label,
            ))
        except (KeyError, TypeError, OverflowError, ValueError) as exc:
            raise ValueError("Incomplete or invalid recurring row") from exc
    return tuple(result)


def render_recurring_editor(plan: Plan, T) -> tuple[RecurringFlow, ...] | None:
    """Edit scheduled flows. Return None when incomplete data must block Run."""
    rows = [
        dict(
            start_month=flow.start_month,
            end_month=flow.end_month,
            frequency=next(k for k, n in PERIODS.items() if n == flow.interval_months),
            amount=flow.amount,
            description=flow.description,
        )
        for flow in plan.recurring_flows
    ]
    table = pd.DataFrame.from_records(
        rows, columns=("start_month", "end_month", "frequency", "amount", "description"),
    )
    with st.expander("📆 " + T("recurring_title"), expanded=False):
        st.caption(T("recurring_intro"))
        st.caption(T("recurring_conventions"))
        edited = st.data_editor(
            table,
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            key="field_recurring_editor",
            column_config={
                "start_month": st.column_config.NumberColumn(
                    T("recurring_start"), min_value=1, max_value=plan.years * 12, step=1,
                    required=True,
                ),
                "end_month": st.column_config.NumberColumn(
                    T("recurring_end"), min_value=1, max_value=plan.years * 12, step=1,
                    required=True,
                ),
                "frequency": st.column_config.SelectboxColumn(
                    T("recurring_frequency"), options=list(PERIODS),
                    required=True,
                ),
                "amount": st.column_config.NumberColumn(
                    T("recurring_amount"), step=1000000 if plan.currency == "VND" else 100,
                    required=True,
                ),
                "description": st.column_config.TextColumn(T("recurring_description")),
            },
        )
        try:
            flows = parse_recurring_rows(edited.to_dict(orient="records"))
            # Dates are validated here against the current, possibly edited horizon.
            if any(flow.end_month > plan.years * 12 or
                   flow.start_month > flow.end_month for flow in flows):
                raise ValueError("Recurring schedule outside projection")
        except ValueError:
            st.warning(T("recurring_invalid"))
            return None
        return flows
