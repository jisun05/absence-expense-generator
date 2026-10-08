from absence_io.auth import get_access_token
from absence_io.timespans import get_timespans
from expense.transformer import summarize_daily_work_times
from receipts.drive import get_receipt_files
from receipts.pdf_generator import create_receipt_pdf
from receipts.processor import process_receipts
from utils.date_utils import get_previous_month


def main():

    # ----------------------------------------
    # 1. 이전 달 구하기
    # ----------------------------------------

    year, month = get_previous_month()

    print(
        f"{year}-{month:02d} searching DATA"
    )

    # ----------------------------------------
    # 2. absence.io 근무 기록 가져오기
    # ----------------------------------------

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
            f"({item['hours']}시간 "
            f"{item['minutes']}분)",
        )

    # ----------------------------------------
    # 3. Google Drive 영수증 가져오기
    # ----------------------------------------

    receipt_files = get_receipt_files()

    print(
        f"\nFound {len(receipt_files)} "
        f"receipt files in Google Drive."
    )

    # ----------------------------------------
    # 4. 근무 기록 + 영수증 처리
    # ----------------------------------------

    receipt_summary = process_receipts(
        receipt_files=receipt_files,
        daily_work_times=daily_work_times,
        year=year,
        month=month,
    )

    # ----------------------------------------
    # 5. 식대 청구 결과 출력
    # ----------------------------------------

    print("\nMeal expenses:")

    for item in receipt_summary["receipts"]:
        print(
            f"{item['date']} "
            f"receipt: €{item['receipt_amount']:.2f} "
            f"reimbursement: "
            f"€{item['reimbursement']:.2f}"
        )

    print(
        "\nTotal reimbursement: "
        f"€{receipt_summary['total_reimbursement']:.2f}"
    )

    # ----------------------------------------
    # 6. 청구 대상 영수증만 PDF 생성
    # ----------------------------------------

    receipt_files_for_pdf = [
        {
            "id": item["file_id"],
            "name": item["filename"],
        }
        for item in receipt_summary["receipts"]
    ]

    if receipt_files_for_pdf:
        create_receipt_pdf(
            receipt_files_for_pdf,
            f"output/receipts_"
            f"{year}_{month:02d}.pdf",
        )

    else:
        print(
            "\nNo eligible receipts found. "
            "PDF was not created."
        )


if __name__ == "__main__":
    main()