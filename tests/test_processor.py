from datetime import date
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from receipts.processor import process_receipts


def test_process_only_matching_receipts():
    receipt_files = [
        {
            "id": "file-1",
            "name": "1.jpg",
        },
        {
            "id": "file-2",
            "name": "3.jpg",
        },
    ]

    daily_work_times = [
        {
            "date": date(2026, 9, 1),
        },
        {
            "date": date(2026, 9, 2),
        },
        {
            "date": date(2026, 9, 3),
        },
    ]

    def fake_download_receipt(file_id):
        return BytesIO()

    with patch(
        "receipts.processor.download_receipt",
        side_effect=fake_download_receipt,
    ), patch(
        "receipts.processor.Image.open",
    ) as mock_image_open, patch(
        "receipts.processor.get_receipt_amount",
        return_value=Decimal("7.80"),
    ):

        mock_image = mock_image_open.return_value

        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert len(result["receipts"]) == 2
    assert result["receipts"][0]["date"] == "2026-09-01"
    assert result["receipts"][1]["date"] == "2026-09-03"
    assert result["total_reimbursement"] == Decimal("15.60")
    assert mock_image.close.call_count == 2


def test_ignore_invalid_receipt_filename():
    receipt_files = [
        {
            "id": "file-1",
            "name": "abc.jpg",
        },
        {
            "id": "file-2",
            "name": "1.jpg",
        },
    ]

    daily_work_times = [
        {
            "date": date(2026, 9, 1),
        },
    ]

    with patch(
        "receipts.processor.download_receipt",
        return_value=BytesIO(),
    ), patch(
        "receipts.processor.Image.open",
    ), patch(
        "receipts.processor.get_receipt_amount",
        return_value=Decimal("5.50"),
    ):

        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert len(result["receipts"]) == 1
    assert result["receipts"][0]["filename"] == "1.jpg"


def test_receipts_are_sorted_by_day():
    receipt_files = [
        {
            "id": "file-3",
            "name": "3.jpg",
        },
        {
            "id": "file-1",
            "name": "1.jpg",
        },
    ]

    daily_work_times = [
        {
            "date": date(2026, 9, 3),
        },
        {
            "date": date(2026, 9, 1),
        },
    ]

    with patch(
        "receipts.processor.download_receipt",
        return_value=BytesIO(),
    ), patch(
        "receipts.processor.Image.open",
    ), patch(
        "receipts.processor.get_receipt_amount",
        return_value=Decimal("5.00"),
    ):

        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert result["receipts"][0]["day"] == 1
    assert result["receipts"][1]["day"] == 3