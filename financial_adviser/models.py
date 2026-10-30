"""Validated domain models. Monetary amounts use the scenario's single currency."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math

from .households import AdultBudget, ChildBudget, DependentBudget, validate_household


@dataclass(frozen=True)
class OneOff:
    month: int  # 1 = first projected month
    amount: float  # positive = inflow, negative = outflow
    description: str = ""


@dataclass(frozen=True)
class RecurringFlow:
    """Signed cash flow repeated at an exact number of calendar months.

    start_month and end_month are inclusive, one-based projection month numbers.
    Interval is 1 (monthly), 3 (quarterly), or 12 (yearly). An amount below
    zero is a payment; a positive amount is income. There is no implicit
    inflation adjustment and no transfer between investment accounts.
    """
    start_month: int
    end_month: int
    interval_months: int
    amount: float
    description: str = ""


@dataclass(frozen=True)
class LifeEvent:
    """Explicit financial consequences of a life event; no inferred probabilities.

    first_month: first projected month (1-based); duration_months includes first month.
    monthly_expense: extra recurring expenses (>= 0, scenario currency).
    monthly_income_change: signed difference in net monthly income.
    upfront_cost: non-negative one-time outflow at the first month.
    """
    category: str
    label: str
    first_month: int
    duration_months: int
    monthly_expense: float = 0.0
    monthly_income_change: float = 0.0
    upfront_cost: float = 0.0


@dataclass(frozen=True)
class Plan:
    country: str = "FR"
    currency: str = "EUR"
    start_year: int = 2026
    years: int = 20
    initial_cash: float = 12000.0
    initial_investments: float = 8000.0
    initial_property_value: float = 0.0  # existing real estate explicitly entered; not bought by the simulation
    initial_other_assets: float = 0.0  # existing non-liquid assets; fixed nominal value
    property_growth_pct: float = 0.0  # assumed annual change in property value, not income
    monthly_income: float = 3000.0  # already net of salary tax and contributions
    monthly_expenses: float = 2000.0  # excludes loan repayment and transfers to investments
    monthly_investment: float = 400.0  # transfer from cash; not additional income
    income_growth_pct: float = 2.0
    expense_growth_pct: float = 2.0
    cash_return_pct: float = 1.0
    investment_return_pct: float = 5.0
    investment_volatility_pct: float = 15.0
    inflation_pct: float = 2.0
    loan_balance: float = 0.0  # outstanding debt only: no property asset is inferred
    loan_apr_pct: float = 3.5
    loan_years: int = 20  # remaining loan term
    goal: float = 100000.0
    one_offs: tuple[OneOff, ...] = field(default_factory=tuple)
    recurring_flows: tuple[RecurringFlow, ...] = field(default_factory=tuple)
    life_events: tuple[LifeEvent, ...] = field(default_factory=tuple)
    children: tuple[ChildBudget, ...] = field(default_factory=tuple)
    adults: tuple[AdultBudget, ...] = field(default_factory=tuple)
    dependents: tuple[DependentBudget, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.country not in {"FR", "VN"}:
            raise ValueError("Unsupported country (FR / VN).")
        if self.currency not in {"EUR", "VND"}:
            raise ValueError("Unsupported currency (EUR / VND).")
        if not 2020 <= self.start_year <= 2100 or not 1 <= self.years <= 60:
            raise ValueError("Start year must be 2020–2100 and horizon 1–60 years.")
        values = asdict(self)
        for name, value in values.items():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")
        for key in ("initial_cash", "initial_investments", "initial_property_value",
                    "initial_other_assets", "monthly_income", "monthly_expenses",
                    "monthly_investment", "loan_balance", "goal"):
            if getattr(self, key) < 0:
                raise ValueError(f"{key} must be non-negative.")
        if not 0 <= self.investment_volatility_pct <= 100:
            raise ValueError("Investment volatility must be in [0, 100]%.")
        for key in ("cash_return_pct", "investment_return_pct", "property_growth_pct", "inflation_pct",
                    "income_growth_pct", "expense_growth_pct"):
            if not -99 < getattr(self, key) <= 200:
                raise ValueError(f"{key} must be in (-99, 200]%.")
        if not 0 <= self.loan_apr_pct <= 100 or not 1 <= self.loan_years <= 60:
            raise ValueError("Invalid loan APR or term.")
        for item in self.life_events:
            if not isinstance(item, LifeEvent):
                raise ValueError("Invalid life event type")
            if not item.category.strip() or not item.label.strip() or len(item.label) > 120:
                raise ValueError("Life events need a category and a short label")
            if (not isinstance(item.first_month, int) or not isinstance(item.duration_months, int)
                    or item.first_month < 1 or item.duration_months < 1
                    or item.first_month + item.duration_months - 1 > self.years * 12):
                raise ValueError("Life event must fit within the projection horizon")
            for value in (item.monthly_expense, item.monthly_income_change, item.upfront_cost):
                if not math.isfinite(value):
                    raise ValueError("Life event amounts must be finite")
            if item.monthly_expense < 0 or item.upfront_cost < 0:
                raise ValueError("Life event costs must be positive or zero")
        validate_household(self)
        for event in self.one_offs:
            if not isinstance(event.month, int) or not 1 <= event.month <= self.years * 12:
                raise ValueError("One-off month must be in projection horizon.")
            if not math.isfinite(event.amount):
                raise ValueError("One-off amount must be finite.")

        if not isinstance(self.recurring_flows, (list, tuple)) or len(self.recurring_flows) > 100:
            raise ValueError("At most 100 recurring flows are allowed")
        for flow in self.recurring_flows:
            if not isinstance(flow, RecurringFlow):
                raise ValueError("Invalid recurring cash flow")
            if (any(isinstance(value, bool) or not isinstance(value, int)
                    for value in (flow.start_month, flow.end_month, flow.interval_months))
                    or not (1 <= flow.start_month <= flow.end_month <= self.years * 12)
                    or flow.interval_months not in (1, 3, 12)):
                raise ValueError("Invalid recurring period or dates")
            if (isinstance(flow.amount, bool) or not isinstance(flow.amount, (float, int))
                    or not math.isfinite(flow.amount)):
                raise ValueError("Invalid recurring cash amount")
            if not isinstance(flow.description, str) or len(flow.description) > 120:
                raise ValueError("Invalid recurring description")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> "Plan":
        allowed = set(cls.__dataclass_fields__)
        if not isinstance(raw, dict) or set(raw) - allowed:
            raise ValueError("Unexpected or invalid scenario field.")
        data = dict(raw)
        if "life_events" in data:
            if not isinstance(data["life_events"], (list, tuple)) or len(data["life_events"]) > 100:
                raise ValueError("life_events must be a list of at most 100 items")
            data["life_events"] = tuple(LifeEvent(**x) for x in data["life_events"])
        if "children" in data:
            if (not isinstance(data["children"], (list, tuple)) or len(data["children"]) > 12
                    or any(not isinstance(x, dict) for x in data["children"])):
                raise ValueError("Invalid children list")
            data["children"] = tuple(ChildBudget(**{
                **x,
                "living": tuple(x.get("living", (0.,) * 5)),
                "care_education": tuple(x.get("care_education", (0.,) * 5)),
            }) for x in data["children"])
        if "adults" in data:
            if (not isinstance(data["adults"], (list, tuple)) or len(data["adults"]) > 8
                    or any(not isinstance(x, dict) for x in data["adults"])):
                raise ValueError("Invalid adults list")
            data["adults"] = tuple(AdultBudget(**{
                **x, "expenses_by_age": tuple(x.get("expenses_by_age", (0.,) * 4)),
            }) for x in data["adults"])
        if "dependents" in data:
            if (not isinstance(data["dependents"], (list, tuple)) or len(data["dependents"]) > 12
                    or any(not isinstance(x, dict) for x in data["dependents"])):
                raise ValueError("Invalid dependents list")
            data["dependents"] = tuple(DependentBudget(**x) for x in data["dependents"])
        if "recurring_flows" in data:
            if (not isinstance(data["recurring_flows"], (list, tuple))
                    or len(data["recurring_flows"]) > 100
                    or any(not isinstance(x, dict) for x in data["recurring_flows"])):
                raise ValueError("Invalid recurring flows list")
            data["recurring_flows"] = tuple(RecurringFlow(**x) for x in data["recurring_flows"])
        if "one_offs" in data:
            if not isinstance(data["one_offs"], (list, tuple)):
                raise ValueError("one_offs must be a list.")
            data["one_offs"] = tuple(OneOff(**x) for x in data["one_offs"])
        plan = cls(**data)
        plan.validate()
        return plan
