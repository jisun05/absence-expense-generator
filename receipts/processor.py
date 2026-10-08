import os
from decimal import Decimal

from PIL import Image

from receipts.drive import download_receipt
from receipts.parser import get_receipt_amount
from expense.calculator import calculate_meal_reimbursement


def process_receipts(
    receipt_files,
    daily_work_times,
    year,
    month,
):
    """
    근무 기록이 있는 날짜 중
    Google Drive에 Canteen 영수증이 있는 날짜만
    식대 청구 대상으로 처리한다.
    """

    # ----------------------------------------
    # 1. Google Drive 영수증을 날짜별로 매핑
    # ----------------------------------------

    receipt_by_date = {}

    for file in receipt_files:
        filename = file["name"]

        # 예: 27.jpg -> 27
        filename_without_extension = os.path.splitext(filename)[0]

        try:
            day = int(filename_without_extension)
        except ValueError:
            # 숫자가 아닌 파일명은 무시
            continue

        receipt_date = f"{year}-{month:02d}-{day:02d}"

        receipt_by_date[receipt_date] = file

    # ----------------------------------------
    # 2. 근무 기록을 기준으로 처리
    # ----------------------------------------

    receipts = []
    total_reimbursement = Decimal("0.00")

    for work_day in daily_work_times:

        work_date = work_day["date"].isoformat()

        # 근무 기록은 있지만 영수증이 없으면 제외
        if work_date not in receipt_by_date:
            continue

        file = receipt_by_date[work_date]

        print(
            f"\nProcessing receipt: "
            f"{work_date} - {file['name']}"
        )

        buffer = download_receipt(file["id"])

        try:
            image = Image.open(buffer)

            # OCR
            receipt_amount = get_receipt_amount(image)

            # 실제 영수증 금액 그대로 청구
            reimbursement = calculate_meal_reimbursement(
                receipt_amount
            )

            total_reimbursement += reimbursement

            receipts.append(
                {
                    "date": work_date,
                    "day": work_day["date"].day,
                    "filename": file["name"],
                    "file_id": file["id"],
                    "receipt_amount": receipt_amount,
                    "reimbursement": reimbursement,
                }
            )

        finally:
            image.close()
            buffer.close()

    # 날짜순 정렬
    receipts.sort(
        key=lambda item: item["day"]
    )

    return {
        "receipts": receipts,
        "total_reimbursement": total_reimbursement,
    }