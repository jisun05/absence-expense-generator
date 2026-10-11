import os
from decimal import Decimal

from PIL import Image

from receipts.drive import download_receipt
from receipts.parser import (
    extract_receipt_amount,
    extract_receipt_date,
    extract_text_from_image,
)
from expense.calculator import calculate_meal_reimbursement


from decimal import Decimal

from PIL import Image

from receipts.drive import download_receipt
from receipts.parser import (
    extract_receipt_amount,
    extract_receipt_date,
    extract_text_from_image,
)
from expense.calculator import calculate_meal_reimbursement


def process_receipts(
    receipt_files,
    daily_work_times,
    year,
    month,
):
    """
    근무 기록과 영수증의 실제 날짜를 비교

    조건:
    1.영수증 날짜와 근무 기록 날짜가 같아야 함
    2.근무시간이 8시간 이상
    3.조건을 만족하는 영수증만 식대 청구 대상
    """

    # 1. 근무 기록을 날짜별로 매핑

    work_by_date = {
        work_day["date"].isoformat(): work_day
        for work_day in daily_work_times
    }


    # 2. 영수증 OCR 및 날짜 검증
    receipts = []
    total_reimbursement = Decimal("0.00")

    for file in receipt_files:
        filename = file["name"]

        print(f"\nProcessing receipt: {filename}")

        buffer = download_receipt(file["id"])

        try:
            with Image.open(buffer) as image:
                # OCR 텍스트 추출
                text = extract_text_from_image(image)

                print("===== OCR TEXT =====")
                print(text)
                print("====================")

                # 실제 영수증 날짜와 금액 추출
                receipt_date = extract_receipt_date(text)
                receipt_amount = extract_receipt_amount(text)

            # 요청한 연월 이외의 영수증은 제외
            if receipt_date.year != year or receipt_date.month != month:
                print(
                    f"Skipping {filename}: "
                    f"receipt date {receipt_date} "
                    f"is outside the requested month."
                )
                continue

            receipt_date_str = receipt_date.isoformat()

            # 해당 날짜의 근무 기록이 없으면 제외
            work_day = work_by_date.get(receipt_date_str)

            if work_day is None:
                print(
                    f"Skipping {filename}: "
                    f"no work record for {receipt_date_str}."
                )
                continue

            # 근무 시간 8시간 미만이면 제외
            total_minutes = work_day.get("total_minutes")

            if total_minutes is None:
                hours = work_day.get("hours", 0)
                minutes = work_day.get("minutes", 0)
                total_minutes = hours * 60 + minutes

            if total_minutes < 8 * 60:
                print(
                    f"Skipping {filename}: "
                    f"work duration is less than 8 hours."
                )
                continue

            # 실제 영수증 금액 그대로 청구
            reimbursement = calculate_meal_reimbursement(
                receipt_amount
            )

            total_reimbursement += reimbursement

            receipts.append(
                {
                    "date": receipt_date_str,
                    "day": receipt_date.day,
                    "filename": filename,
                    "file_id": file["id"],
                    "receipt_amount": receipt_amount,
                    "reimbursement": reimbursement,
                }
            )

        except ValueError as error:
            print(
                f"Skipping {filename}: "
                f"could not process receipt - {error}"
            )

        finally:
            buffer.close()

    # 날짜순 정렬
    receipts.sort(
        key=lambda item: item["date"]
    )

    return {
        "receipts": receipts,
        "total_reimbursement": total_reimbursement,
    }