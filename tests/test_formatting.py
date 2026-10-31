from financial_adviser.formatting import NBSP, format_money


def test_french_uses_spaces_and_decimal_comma():
    assert format_money(416145.912, "EUR", "fr") == f"416{NBSP}145,91{NBSP}€"


def test_english_puts_euro_first():
    assert format_money(-1234.5, "EUR", "en") == "-€1,234.50"


def test_vietnamese_dong_has_dots_and_no_decimals():
    assert format_money(1234567.4, "VND", "vi") == f"1.234.567{NBSP}₫"


def test_rounding_to_zero_has_no_minus_sign():
    assert format_money(-0.001, "EUR", "fr") == f"0,00{NBSP}€"


def test_non_finite_amount_is_a_dash():
    assert format_money(float("nan"), "EUR", "fr") == "—"


def test_decimal_follows_language():
    from financial_adviser.formatting import format_decimal
    assert format_decimal(6.04, 1, "fr") == "6,0"
    assert format_decimal(6.04, 1, "en") == "6.0"
    assert format_decimal(1234.5, 1, "vi") == "1.234,5"
