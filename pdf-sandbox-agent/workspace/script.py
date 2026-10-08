import sys, json, traceback
from pathlib import Path
pdf_path = Path('/workspace/input/sample.pdf')
if not pdf_path.is_file():
    print('PDF not found')
    sys.exit(0)
# Try using pypdf
try:
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    print(f'Number of pages: {num_pages}')
    # page numbers are 0-indexed
    target = 10  # page 11
    if target < num_pages:
        page = reader.pages[target]
        text = page.extract_text()
        print('--- Page 11 Text Start ---')
        print(text)
        print('--- Page 11 Text End ---')
    else:
        print('Page 11 out of range')
except Exception as e:
    print('Error using pypdf:', e)
    traceback.print_exc()
    # fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            if target < len(pdf.pages):
                page = pdf.pages[target]
                text = page.extract_text()
                print('--- Page 11 Text (pdfplumber) Start ---')
                print(text)
                print('--- Page 11 Text (pdfplumber) End ---')
            else:
                print('Page 11 out of range in pdfplumber')
    except Exception as e2:
        print('Error using pdfplumber:', e2)
        traceback.print_exc()