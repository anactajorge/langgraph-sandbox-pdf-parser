# 1. Start from an official lightweight Python Linux image
FROM python:3.11-slim

# 2. Prevent Python from buffering terminal logs (ensures output shows up immediately)
ENV PYTHONUNBUFFERED=1

# 3. Install system-level tools needed by PDF/image extractors
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 4. Install the Python PDF libraries your sandbox will need
RUN pip install --no-cache-dir \
    pypdf \
    pdfplumber \
    pymupdf

# 5. Set the default working directory inside the container
WORKDIR /workspace