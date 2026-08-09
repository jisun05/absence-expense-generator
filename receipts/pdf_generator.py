import os

from PIL import Image

from receipts.drive import download_receipt


def create_receipt_pdf(files, output_path):
    images = []

    if not files:
        raise ValueError("No receipt images found")

    # output 폴더가 없으면 자동 생성
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    for file in files:
        print(f'Downloading {file["name"]}...')

        buffer = download_receipt(file["id"])

        try:
            image = Image.open(buffer)

            # PDF 저장을 위해 RGB로 변환
            if image.mode != "RGB":
                image = image.convert("RGB")
            else:
                image = image.copy()

            images.append(image)

        finally:
            buffer.close()

    # 첫 이미지를 기준으로 나머지 이미지를 이어 붙임
    first_image = images[0]

    first_image.save(
        output_path,
        "PDF",
        save_all=True,
        append_images=images[1:],
    )

    # 메모리 정리
    for image in images:
        image.close()

    print(f"\nPDF created: {output_path}")