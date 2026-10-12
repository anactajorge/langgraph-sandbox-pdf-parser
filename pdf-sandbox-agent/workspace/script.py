"""
Search for keywords in Main Topic 1.pdf
"""
import re, sys
from pathlib import Path
pdf_path = Path('/workspace/input/Main Topic 1.pdf')
if not pdf_path.is_file():
    print('File not found')
    sys.exit(1)

from pypdf import PdfReader
reader = PdfReader(str(pdf_path))
found = []
for i, page in enumerate(reader.pages):
    text = page.extract_text() or ''
    if re.search(r'layer', text, re.IGNORECASE) or re.search(r'overview', text, re.IGNORECASE) or re.search(r'workflow', text, re.IGNORECASE):
        found.append((i+1, text[:500]))
print('Pages with matches:', len(found))
for num, snippet in found:
    print('\n--- Page', num, '---')
    print(snippet)
