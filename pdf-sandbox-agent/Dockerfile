# 1. Start from an official lightweight Python Linux image
FROM python:3.11-slim

# 2. Prevent Python from buffering terminal logs
ENV PYTHONUNBUFFERED=1

# 3. Install system-level tools needed by PDF/image extractors & OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 4. Install the Python PDF & OCR libraries
RUN pip install --no-cache-dir \
    pypdf \
    pdfplumber \
    pymupdf \
    pytesseract \
    pillow

# 5. Set the default working directory inside the container
WORKDIR /workspace