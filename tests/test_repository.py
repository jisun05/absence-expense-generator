from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from database.repository import (
    save_expense,
    save_receipt,
    save_work_record,
)


@patch("database.repository.get_connection")
def test_save_work_record(mock_get_connection):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    mock_get_connection.return_value.__enter__.return_value = connection

    work_day = {
        "date": date(2026, 9, 1),
        "start": datetime(2026, 9, 1, 9, 0),
        "end": datetime(2026, 9, 1, 18, 0),
        "total_minutes": 540,
    }

    save_work_record(work_day)

    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()


@patch("database.repository.get_connection")
def test_save_receipt(mock_get_connection):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    mock_get_connection.return_value.__enter__.return_value = connection

    receipt = {
        "date": "2026-09-01",
        "filename": "1.jpg",
        "file_id": "test-id",
        "receipt_amount": Decimal("6.50"),
    }

    save_receipt(receipt)

    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()


@patch("database.repository.get_connection")
def test_save_expense(mock_get_connection):
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    mock_get_connection.return_value.__enter__.return_value = connection

    expense = {
        "date": "2026-09-01",
        "receipt_amount": Decimal("6.50"),
        "reimbursement": Decimal("6.50"),
    }

    save_expense(expense)

    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()