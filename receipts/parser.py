import os
import re
from decimal import Decimal
from datetime import datetime

import pytesseract


# Tesseract 설치 경로
# 환경 변수가 설정된 경우 해당 경로를 사용
# 그렇지 않으면 시스템의 기본 실행 경로를 사용한다.
tesseract_path = os.getenv("TESSERACT_CMD")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


DATE_PATTERNS = [
    # 예: 11.09.2026 또는 11/09/2026
    r"\b(\d{2}[./-]\d{2}[./-]\d{4})\b",

    # 예: 2026-09-11
    r"\b(\d{4}-\d{2}-\d{2})\b",

    # 예: 01.09.26 또는 01/09/26
    r"\b(\d{2}[./-]\d{2}[./-]\d{2})\b",
]

AMOUNT_PATTERNS = [
    # 회사 식당
    r"Total Transaction Amount[:\s-]*([0-9]+[,.][0-9]{2})",
    r"Total Due[:\s-]*([0-9]+[,.][0-9]{2})",

    # REWE
    # r"SUMME\s+(?:EUR\s+)?([0-9]+[,.][0-9]{2})",
    # r"Betrag\s+EUR\s+([0-9]+[,.][0-9]{2})",
]


def extract_text_from_image(image):
    return pytesseract.image_to_string(
        image,
        lang="eng+deu",
    )


def extract_receipt_amount(text):

    for pattern in AMOUNT_PATTERNS:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            amount_text = match.group(1).replace(",", ".")
            return Decimal(amount_text)

    raise ValueError("Could not find receipt amount")


def extract_receipt_date(text):

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)

        if not match:
            continue

        date_text = match.group(1)

        for date_format in (
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d.%m.%y",
            "%d/%m/%y",
            "%d-%m-%y",
        ):
            try:
                return datetime.strptime(
                    date_text,
                    date_format,
                ).date()
            except ValueError:
                continue

    raise ValueError("Could not find receipt date")


def get_receipt_amount(image):

    text = extract_text_from_image(image)

    print("=OCR TEXT=")
    print(text)


    return extract_receipt_amount(text)