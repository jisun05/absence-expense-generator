FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY batch ./batch
COPY absence_io ./absence_io
COPY expense ./expense
COPY receipts ./receipts
COPY utils ./utils
COPY database ./database
COPY tests ./tests
COPY main.py .

RUN mkdir -p /app/output

CMD ["python", "main.py"]