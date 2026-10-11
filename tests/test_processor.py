from datetime import date
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest

from receipts.processor import process_receipts


def create_receipt_files(*days):
    """테스트용 영수증 파일 목록 생성"""
    return [
        {
            "id": f"file-{day}",
            "name": f"{day}.jpg",
        }
        for day in days
    ]


def create_work_record(work_date, total_minutes=480):
    """테스트용 근무 기록 생성"""
    return {
        "date": date.fromisoformat(work_date),
        "total_minutes": total_minutes,
    }


def setup_receipt_mocks(mock_image_open, receipt_dates, amount):
    """OCR 날짜와 금액 추출을 모킹"""

    mock_image_open.return_value.__enter__.return_value = mock_image_open.return_value

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=receipt_dates,
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal(amount),
        ),
    ):
        yield


def test_process_only_matching_receipts():
    receipt_files = create_receipt_files(1, 3)

    daily_work_times = [
        create_work_record("2026-09-01"),
        create_work_record("2026-09-02"),
        create_work_record("2026-09-03"),
    ]

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch(
            "receipts.processor.Image.open",
        ),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=[
                date(2026, 9, 1),
                date(2026, 9, 3),
            ],
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal("7.80"),
        ),
    ):
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


def test_receipt_without_matching_work_record_is_excluded():
    receipt_files = create_receipt_files(1, 2)

    daily_work_times = [
        create_work_record("2026-09-01"),
    ]

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch("receipts.processor.Image.open"),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=[
                date(2026, 9, 1),
                date(2026, 9, 2),
            ],
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal("5.50"),
        ),
    ):
        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert len(result["receipts"]) == 1
    assert result["receipts"][0]["date"] == "2026-09-01"


def test_work_duration_less_than_eight_hours_is_excluded():
    receipt_files = create_receipt_files(1, 2)

    daily_work_times = [
        create_work_record("2026-09-01", total_minutes=479),
        create_work_record("2026-09-02", total_minutes=480),
    ]

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch("receipts.processor.Image.open"),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=[
                date(2026, 9, 1),
                date(2026, 9, 2),
            ],
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal("6.50"),
        ),
    ):
        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert len(result["receipts"]) == 1
    assert result["receipts"][0]["date"] == "2026-09-02"
    assert result["total_reimbursement"] == Decimal("6.50")


def test_receipts_are_sorted_by_date():
    receipt_files = create_receipt_files(3, 1)

    daily_work_times = [
        create_work_record("2026-09-03"),
        create_work_record("2026-09-01"),
    ]

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch("receipts.processor.Image.open"),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=[
                date(2026, 9, 3),
                date(2026, 9, 1),
            ],
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal("5.00"),
        ),
    ):
        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert result["receipts"][0]["day"] == 1
    assert result["receipts"][1]["day"] == 3


def test_receipt_outside_requested_month_is_excluded():
    receipt_files = create_receipt_files(1)

    daily_work_times = [
        create_work_record("2026-09-01"),
    ]

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch("receipts.processor.Image.open"),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Mock receipt text",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            return_value=date(2026, 8, 1),
        ),
        patch(
            "receipts.processor.extract_receipt_amount",
            return_value=Decimal("6.50"),
        ),
    ):
        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=daily_work_times,
            year=2026,
            month=9,
        )

    assert result["receipts"] == []
    assert result["total_reimbursement"] == Decimal("0.00")


def test_invalid_receipt_date_is_excluded():
    receipt_files = create_receipt_files(1)

    with (
        patch(
            "receipts.processor.download_receipt",
            return_value=BytesIO(),
        ),
        patch("receipts.processor.Image.open"),
        patch(
            "receipts.processor.extract_text_from_image",
            return_value="Receipt without date",
        ),
        patch(
            "receipts.processor.extract_receipt_date",
            side_effect=ValueError("Could not find receipt date"),
        ),
    ):
        result = process_receipts(
            receipt_files=receipt_files,
            daily_work_times=[
                create_work_record("2026-09-01"),
            ],
            year=2026,
            month=9,
        )

    assert result["receipts"] == []