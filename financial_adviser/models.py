"""Validated domain models. Monetary amounts use the scenario's single currency."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math


@dataclass(frozen=True)
class OneOff:
    month: int  # 1 = first projected month
    amount: float  # positive = inflow, negative = outflow
    description: str = ""


@dataclass(frozen=True)
class Plan:
    country: str = "FR"
    currency: str = "EUR"
    start_year: int = 2026
    years: int = 20
    initial_cash: float = 12000.0
    initial_investments: float = 8000.0
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
        for key in ("initial_cash", "initial_investments", "monthly_income", "monthly_expenses",
                    "monthly_investment", "loan_balance", "goal"):
            if getattr(self, key) < 0:
                raise ValueError(f"{key} must be non-negative.")
        if not 0 <= self.investment_volatility_pct <= 100:
            raise ValueError("Investment volatility must be in [0, 100]%.")
        for key in ("cash_return_pct", "investment_return_pct", "inflation_pct",
                    "income_growth_pct", "expense_growth_pct"):
            if not -99 < getattr(self, key) <= 200:
                raise ValueError(f"{key} must be in (-99, 200]%.")
        if not 0 <= self.loan_apr_pct <= 100 or not 1 <= self.loan_years <= 60:
            raise ValueError("Invalid loan APR or term.")
        for event in self.one_offs:
            if not isinstance(event.month, int) or not 1 <= event.month <= self.years * 12:
                raise ValueError("One-off month must be in projection horizon.")
            if not math.isfinite(event.amount):
                raise ValueError("One-off amount must be finite.")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict) -> "Plan":
        allowed = set(cls.__dataclass_fields__)
        if not isinstance(raw, dict) or set(raw) - allowed:
            raise ValueError("Unexpected or invalid scenario field.")
        data = dict(raw)
        if "one_offs" in data:
            if not isinstance(data["one_offs"], (list, tuple)):
                raise ValueError("one_offs must be a list.")
            data["one_offs"] = tuple(OneOff(**x) for x in data["one_offs"])
        plan = cls(**data)
        plan.validate()
        return plan
