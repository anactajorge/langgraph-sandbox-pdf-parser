from pypdf import PdfReader

reader = PdfReader("/workspace/input/sample.pdf")
print(f"Total Pages: {len(reader.pages)}")
print("--- Page 1 Preview ---")
print(reader.pages[0].extract_text()[:300])