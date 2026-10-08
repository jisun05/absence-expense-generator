from decimal import Decimal

import pytest

from receipts.parser import extract_receipt_amount


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