from io import BytesIO


def read_uploaded_file(uploaded_file):
    """Extract text from PDF, DOCX, TXT, Markdown, or CSV upload."""
    extension = uploaded_file.name.lower().rsplit(".", 1)[-1]
    try:
        data = uploaded_file.getvalue()
        if extension in {"txt", "md", "csv"}:
            return data.decode("utf-8", errors="replace"), ""
        if extension == "pdf":
            from pypdf import PdfReader

            pages = PdfReader(BytesIO(data)).pages
            text = "\n\n".join(page.extract_text() or "" for page in pages)
            if not text.strip():
                return "", f"{uploaded_file.name} appears to have no extractable text. It may be a scanned PDF."
            return text, ""
        if extension == "docx":
            from docx import Document

            document = Document(BytesIO(data))
            return "\n".join(p.text for p in document.paragraphs if p.text.strip()), ""
        return "", f"Unsupported file: {uploaded_file.name}. Please use PDF, DOCX, TXT, MD, or CSV."
    except Exception as error:
        return "", f"Could not read {uploaded_file.name}: {error}"
