from pypdf import PdfReader

def extract_text_from_pdf(file_path: str):
    reader = PdfReader(file_path)

    pages_text = []
    full_text_parts = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages_text.append({
            "page": page_number,
            "text": text
        })
        full_text_parts.append(text)

    full_text = "\n".join(full_text_parts)

    return {
        "page_count": len(reader.pages),
        "full_text": full_text,
        "pages": pages_text
    }