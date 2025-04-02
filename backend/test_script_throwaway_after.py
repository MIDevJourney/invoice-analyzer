from utils.pdf_processor import extract_text_from_pdf

files = [
    "../tech_solutions_invoice.pdf",
    "../office_supplies_invoice.pdf",
    "../consulting_services_invoice.pdf"
]

for f in files:
    print(f"\n--- {f} ---")
    print(extract_text_from_pdf(f)[:500])  # First 500 chars
