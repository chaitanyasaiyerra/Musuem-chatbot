import pypdf
import sys

try:
    reader = pypdf.PdfReader('Reviewww.pdf')
    with open('Reviewww_extracted.txt', 'w', encoding='utf-8') as f:
        for i, page in enumerate(reader.pages):
            f.write(f'\n--- Page {i+1} ---\n')
            f.write(page.extract_text() + '\n')
    print("Extraction successful.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
