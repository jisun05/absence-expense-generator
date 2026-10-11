from decimal import Decimal

import pytest

from receipts.parser import extract_receipt_amount,extract_receipt_date


def test_extract_total_transaction_amount():
    text = "Total Transaction Amount: 7.80"

    result = extract_receipt_amount(text)

    assert result == Decimal("7.80")


def test_extract_total_due():
    text = "Total Due: 12.50"

    result = extract_receipt_amount(text)

    assert result == Decimal("12.50")


def test_extract_amount_with_comma():
    text = "Total Due: 7,80"

    result = extract_receipt_amount(text)

    assert result == Decimal("7.80")


def test_raise_error_when_amount_not_found():
    text = "Receipt without amount"

    with pytest.raises(ValueError):
        extract_receipt_amount(text)

def test_extract_receipt_date_with_dots():
    text = "Date: 11.09.2026"

    result = extract_receipt_date(text)

    assert result.isoformat() == "2026-09-11"


def test_extract_receipt_date_with_slashes():
    text = "Date: 11/09/2026"

    result = extract_receipt_date(text)

    assert result.isoformat() == "2026-09-11"


def test_extract_receipt_date_with_iso_format():
    text = "Date: 2026-09-11"

    result = extract_receipt_date(text)

    assert result.isoformat() == "2026-09-11"


def test_extract_receipt_date_with_hyphens():
    text = "Date: 11-09-2026"

    result = extract_receipt_date(text)

    assert result.isoformat() == "2026-09-11"


def test_raise_error_when_date_not_found():
    text = "Receipt without date"

    with pytest.raises(ValueError):
        extract_receipt_date(text)


def test_extract_receipt_date_with_two_digit_year():
    text = "Order Placing Time: 01.09.26 12:10"

    result = extract_receipt_date(text)

    assert result.isoformat() == "2026-09-01"