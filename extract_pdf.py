import pdfplumber
import sys
import os

def extract_pdf(pdf_path, output_txt):
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    extracted_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n\n".join(extracted_pages))

    print("Extraction complete.")
    print(f"Saved to: {output_txt}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_pdf.py <input.pdf> <output.txt>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_txt = sys.argv[2]

    extract_pdf(input_pdf, output_txt)
