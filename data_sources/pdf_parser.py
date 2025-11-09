from PyPDF2 import PdfReader

def parse_pdf(filepath: str) -> str:
    try:
        reader = PdfReader(filepath)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)
    except Exception:
        return ""
