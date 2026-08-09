from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from expense.transformer import summarize_daily_work_times
from receipts.drive import get_receipt_files
from receipts.pdf_generator import create_receipt_pdf
from receipts.processor import process_receipts
from utils.date_utils import get_previous_month


def main():
    year, month = get_previous_month()

    print(f"{year}-{month:02d} searching DATA")

    # absence.io 근무 기록 조회
    token = get_access_token()

    result = get_timespans(
        token=token,
        year=year,
        month=month,
    )

    daily_work_times = summarize_daily_work_times(
        result["data"]
    )

    print("\nWork times:")

    for item in daily_work_times:
        print(
            item["date"],
            item["start"].strftime("%H:%M"),
            "->",
            item["end"].strftime("%H:%M"),
            f'({item["hours"]}시간 {item["minutes"]}분)',
        )

    # Google Drive 영수증 목록 조회
    receipt_files = get_receipt_files()

    # 모든 영수증 OCR + 청구 금액 계산
    receipt_summary = process_receipts(
        receipt_files,
        year,
        month,
    )

    print("\nMeal expenses:")

    for item in receipt_summary["receipts"]:
        print(
            item["date"],
            f'receipt: €{item["receipt_amount"]:.2f}',
            f'reimbursement: €{item["reimbursement"]:.2f}',
        )

    print(
        "\nTotal reimbursement:",
        f'€{receipt_summary["total_reimbursement"]:.2f}',
    )

    # 영수증 PDF 생성
    create_receipt_pdf(
        receipt_files,
        f"output/receipts_{year}_{month:02d}.pdf",
    )


if __name__ == "__main__":
    main()