from pathlib import Path
from app.services.pdf_loader import extract_text_from_pdf


base_path = Path(__file__).parent.parent

pdf_path = base_path / "legal_documents" / "sample.pdf"

print("PDF path:", pdf_path)
print("PDF exists:", pdf_path.exists())

text = extract_text_from_pdf(pdf_path)

print("\nExtracted Text:\n")
print(text[:2000])