from io import BytesIO


def to_docx(markdown_text: str) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_heading("BidForge AI — Tender Response Draft", 0)
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=2)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=1)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:], style="List Bullet")
        else:
            doc.add_paragraph(stripped.replace("**", "").replace("`", ""))
    output = BytesIO()
    doc.save(output)
    return output.getvalue()


def to_pdf(markdown_text: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("BidForge AI — Tender Response Draft", styles["Title"]), Spacer(1, 8)]
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
            continue
        style = styles["Heading2"] if stripped.startswith("## ") else styles["Heading3"] if stripped.startswith("### ") else styles["BodyText"]
        if stripped.startswith("### "):
            stripped = stripped[4:]
        elif stripped.startswith("## "):
            stripped = stripped[3:]
        elif stripped.startswith("# "):
            stripped = stripped[2:]
            style = styles["Heading1"]
        stripped = stripped.replace("**", "").replace("`", "")
        story.append(Paragraph(escape(stripped), style))
    doc.build(story)
    return output.getvalue()
