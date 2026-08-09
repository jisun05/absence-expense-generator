from PIL import Image

from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from expense.transformer import summarize_daily_work_times
from expense.calculator import calculate_meal_reimbursement
from receipts.drive import get_receipt_files, download_receipt
from receipts.parser import get_receipt_amount
from receipts.pdf_generator import create_receipt_pdf
from utils.date_utils import get_previous_month


def main():
    year, month = get_previous_month()

    print(f"{year}-{month:02d} searching DATA")

    token = get_access_token()
    result = get_timespans(
        token=token,
        year=year,
        month=month,
    )

    daily_work_times = summarize_daily_work_times(result["data"])

    for item in daily_work_times:
        print(
            item["date"],
            item["start"].strftime("%H:%M"),
            "->",
            item["end"].strftime("%H:%M"),
            f'({item["hours"]}시간 {item["minutes"]}분)',
        )

    # Google Drive
    receipt_files = get_receipt_files()

    # 첫 번째 영수증 한 장만 OCR 테스트
    file = receipt_files[18]

    buffer = download_receipt(file["id"])
    image = Image.open(buffer)

    amount = get_receipt_amount(image)
    reimbursement = calculate_meal_reimbursement(amount)

    print("\nOCR TEST")
    print("file:", file["name"])
    print("receipt amount:", amount)
    print("reimbursement:", reimbursement)

    image.close()
    buffer.close()

    print("\nReceipts:")
    for file in receipt_files:
        print(file["name"])

    # OCR 테스트 성공 후 다시 켜도 됨
    # create_receipt_pdf(
    #     receipt_files,
    #     f"output/receipts_{year}_{month:02d}.pdf"
    # )


if __name__ == "__main__":
    main()