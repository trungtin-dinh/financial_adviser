"""Display formatting of amounts according to the interface language.

Only presentation changes: exported files keep machine-readable numbers.
"""
from __future__ import annotations

import math

NBSP = " "  # keeps "1 234 €" on one line in metrics and narrow columns

# (thousands separator, decimal separator) for each interface language.
_SEPARATORS = {"fr": (NBSP, ","), "en": (",", "."), "vi": (".", ",")}


def format_money(amount: float, currency: str, lang: str = "fr") -> str:
    """Amount with the language's separators; VND has no decimals.

    fr: 1 234,56 €   en: €1,234.56   vi: 1.234,56 €   (VND: 1 234 567 ₫ ...)
    """
    if not math.isfinite(amount):
        return "—"
    thousands, decimal = _SEPARATORS.get(lang, _SEPARATORS["fr"])
    digits = 0 if currency == "VND" else 2
    text = f"{abs(amount):,.{digits}f}"
    text = text.replace(",", "\0").replace(".", decimal).replace("\0", thousands)
    sign = "-" if amount < 0 and float(text.replace(thousands, "").replace(decimal, ".")) != 0 else ""
    if currency == "EUR" and lang == "en":
        return f"{sign}€{text}"
    symbol = "₫" if currency == "VND" else "€"
    return f"{sign}{text}{NBSP}{symbol}"


def format_decimal(value: float, digits: int = 1, lang: str = "fr") -> str:
    """Plain number (ratio, months) with the language's decimal separator."""
    if not math.isfinite(value):
        return "—"
    thousands, decimal = _SEPARATORS.get(lang, _SEPARATORS["fr"])
    text = f"{value:,.{digits}f}"
    return text.replace(",", "\0").replace(".", decimal).replace("\0", thousands)
