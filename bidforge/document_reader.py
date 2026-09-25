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
                try:
                    from pdf2image import convert_from_bytes
                    import pytesseract

                    images = convert_from_bytes(data, dpi=180, first_page=1, last_page=min(len(pages), 30))
                    text = "\n\n".join(pytesseract.image_to_string(image) for image in images)
                    if not text.strip():
                        return "", f"OCR found no readable text in {uploaded_file.name}. Check the scan or paste the relevant text."
                    return text, f"{uploaded_file.name} was scanned with OCR; verify the extracted text carefully. OCR is limited to the first 30 pages."
                except Exception as ocr_error:
                    return "", f"{uploaded_file.name} appears scanned and OCR could not read it ({ocr_error}). Upload a searchable PDF or paste its text."
            return text, ""
        if extension == "docx":
            from docx import Document

            document = Document(BytesIO(data))
            chunks = [p.text for p in document.paragraphs if p.text.strip()]
            for table in document.tables:
                chunks.extend(" | ".join(cell.text.strip() for cell in row.cells) for row in table.rows)
            return "\n".join(chunks), ""
        return "", f"Unsupported file: {uploaded_file.name}. Please use PDF, DOCX, TXT, MD, or CSV."
    except Exception as error:
        return "", f"Could not read {uploaded_file.name}: {error}"
