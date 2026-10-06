#!/usr/bin/env python3
import sys
from pathlib import Path
pdf_path = Path('/workspace/input/sample.pdf')
if not pdf_path.is_file():
    print('PDF not found')
    sys.exit(1)

try:
    import fitz  # pymupdf
    import io
    from PIL import Image
    import pytesseract
    doc = fitz.open(str(pdf_path))
    if doc.page_count < 5:
        print('Only', doc.page_count, 'pages')
        sys.exit(0)
    page = doc.load_page(4)
    # render at 300 DPI
    zoom = 300/72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    # OCR
    text = pytesseract.image_to_string(img)
    print('--- OCR text ---')
    print(text.strip() if text else '[No OCR text]')
except Exception as e:
    print('Error:', e)
    sys.exit(1)
