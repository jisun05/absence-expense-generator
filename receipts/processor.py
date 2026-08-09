import os
from decimal import Decimal

from PIL import Image

from receipts.drive import download_receipt
from receipts.parser import get_receipt_amount
from expense.calculator import calculate_meal_reimbursement


def process_receipts(receipt_files, year, month):
    receipts = []
    total_reimbursement = Decimal("0.00")

    for file in receipt_files:
        filename = file["name"]

        # 27.jpg 또는 27 → 27
        day = int(os.path.splitext(filename)[0])

        buffer = download_receipt(file["id"])

        try:
            image = Image.open(buffer)

            # OCR로 실제 영수증 금액 추출
            receipt_amount = get_receipt_amount(image)

            # 최대 €6.50까지만 청구
            reimbursement = calculate_meal_reimbursement(
                receipt_amount
            )

            total_reimbursement += reimbursement

            receipts.append(
                {
                    "date": f"{year}-{month:02d}-{day:02d}",
                    "day": day,
                    "filename": filename,
                    "receipt_amount": receipt_amount,
                    "reimbursement": reimbursement,
                }
            )

        finally:
            buffer.close()

    receipts.sort(key=lambda item: item["day"])

    return {
        "receipts": receipts,
        "total_reimbursement": total_reimbursement,
    }