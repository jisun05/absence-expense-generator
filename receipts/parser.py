import re
from decimal import Decimal
import pytesseract



# Tesseract 설치 경로
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


AMOUNT_PATTERNS = [
    # 회사 식당
    r"Total Transaction Amount[:\s-]*([0-9]+[,.][0-9]{2})",
    r"Total Due[:\s-]*([0-9]+[,.][0-9]{2})",

    # REWE
    #r"SUMME\s+(?:EUR\s+)?([0-9]+[,.][0-9]{2})",
    #r"Betrag\s+EUR\s+([0-9]+[,.][0-9]{2})",
]


def extract_text_from_image(image):
    """영수증 이미지 → 문자열"""
    return pytesseract.image_to_string(
        image,
        lang="eng",
    )


def extract_receipt_amount(text):
    """OCR 문자열 → 실제 결제 금액"""

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


def get_receipt_amount(image):
    """영수증 이미지 to 실제 결제 금액"""

    text = extract_text_from_image(image)
    print("===== OCR TEXT =====")
    print(text)
    print("====================")

    return extract_receipt_amount(text)

