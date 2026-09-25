import os
import re
import sys

import pandas as pd
import streamlit as st

if sys.version_info >= (3, 14):
    st.error("CrewAI/ChromaDB can fail on Python 3.14. Redeploy this Streamlit app using Python 3.12.")
    st.stop()

from bidforge.agent import draft_response
from bidforge.document_reader import read_uploaded_file
from bidforge.exports import to_docx, to_pdf
from bidforge.memory import add_to_memory, get_memory, reset_memory
from bidforge.web_reader import fetch_public_text


st.set_page_config(page_title="BidForge AI", page_icon="📑", layout="wide")
st.title("📑 BidForge AI")
st.caption("Tender response drafting grounded in tender text and evidence you provide.")

for key, default in {
    "bidforge_memory": [],
    "bidforge_messages": [],
    "bidforge_evidence": [],
    "bidforge_compliance": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def extract_compliance_table(markdown: str) -> pd.DataFrame:
    rows = []
    in_table = False
    for line in markdown.splitlines():
        if line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            if not in_table:
                in_table = True
                continue
            if len(cells) >= 4:
                rows.append(cells[:5] if len(cells) >= 5 else cells[:4] + [""])
        elif in_table:
            break
    columns = ["Requirement", "Source", "Status", "Evidence / next action", "Owner"]
    return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)


with st.sidebar:
    st.header("Tender sources")
    tender_url = st.text_input("Public tender page or PDF link", placeholder="https://…")
    tender_upload = st.file_uploader("Or upload tender", type=["pdf", "docx", "txt", "md"])
    tender_paste = st.text_area("Or paste tender text", height=110)

    st.header("Company sources")
    company_urls = st.text_area("Public company profile links (one URL per line)", height=90, placeholder="https://company.example/about\nhttps://company.example/projects")
    company_uploads = st.file_uploader(
        "Company evidence and required templates",
        type=["pdf", "docx", "txt", "md", "csv"],
        accept_multiple_files=True,
    )
    with st.expander("Company and bid details", expanded=True):
        company_facts = st.text_area("Verified company facts", height=115, placeholder="Name, registration, certifications, references, financial standing, personnel…")
        pricing_facts = st.text_area("Pricing inputs (optional)", height=90, placeholder="Rates, units, currency, quantities, taxes…")
        format_facts = st.text_area("Required template / format / page limits", height=80)

    st.header("Evidence library")
    st.caption("Session-only. Saved evidence is available in this browser session and can be cleared below.")
    with st.expander("Save verified company facts"):
        evidence_note = st.text_area("Verified reusable evidence", placeholder="Example: ISO certificate number, valid-to date, reference project facts…")
        if st.button("Save evidence for this session") and evidence_note.strip():
            st.session_state.bidforge_evidence.append(evidence_note.strip())
            st.success("Saved for this session.")
            st.rerun()
    if st.session_state.bidforge_evidence:
        st.caption(f"{len(st.session_state.bidforge_evidence)} evidence note(s) saved.")
    with st.expander("Session memory"):
        st.caption(f"{len(get_memory())} note(s) · ends with this browser session.")
        note = st.text_input("Add a memory note", placeholder="Example: Bid currency is PKR")
        if st.button("Save memory note") and note.strip():
            add_to_memory(note.strip())
            st.rerun()
        if st.button("Clear session notes and evidence"):
            reset_memory()
            st.session_state.bidforge_evidence = []
            st.rerun()

st.subheader("Choose what BidForge should prepare")
options = [
    "Tender analysis and facts",
    "Compliance checklist",
    "Scope of work and clarification questions",
    "Technical proposal",
    "Financial bid structure",
    "Supporting documents checklist",
    "Final readiness review",
    "Proposal quality review",
]
selected_sections = st.multiselect("Generate sections", options, default=options)

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None
st.info("Groq model: openai/gpt-oss-120b · Add GROQ_API_KEY in Streamlit Cloud → App settings → Secrets.")

if st.button("Read sources and prepare selected sections", type="primary", use_container_width=True):
    if not api_key:
        st.error("GROQ_API_KEY is missing. Add it to Streamlit Cloud Secrets.")
    elif not selected_sections:
        st.error("Select at least one section to generate.")
    elif not (tender_upload or tender_paste.strip() or tender_url.strip()):
        st.error("Provide the tender as an upload, public link, or pasted text.")
    else:
        tender_parts = []
        evidence_parts = []
        source_notes = []
        with st.spinner("Extracting tender and company sources…"):
            if tender_paste.strip():
                tender_parts.append("Pasted tender text\n" + tender_paste.strip())
            if tender_upload:
                text, warning = read_uploaded_file(tender_upload)
                if text.strip():
                    tender_parts.append(f"Uploaded tender: {tender_upload.name}\n{text}")
                if warning:
                    source_notes.append(warning)
            if tender_url.strip():
                try:
                    text, warning = fetch_public_text(tender_url.strip())
                    if text.strip():
                        tender_parts.append("Linked tender source\n" + text)
                    if warning:
                        source_notes.append("Tender link: " + warning)
                except Exception as error:
                    source_notes.append(f"Tender link could not be read: {error}")

            for url in [item.strip() for item in company_urls.splitlines() if item.strip()]:
                try:
                    text, warning = fetch_public_text(url)
                    if text.strip():
                        evidence_parts.append(f"Company link source\n{text}")
                    if warning:
                        source_notes.append(f"Company link {url}: {warning}")
                except Exception as error:
                    source_notes.append(f"Company link {url} could not be read: {error}")
            for uploaded in company_uploads or []:
                text, warning = read_uploaded_file(uploaded)
                if text.strip():
                    evidence_parts.append(f"Uploaded source: {uploaded.name}\n{text}")
                if warning:
                    source_notes.append(warning)
            evidence_parts.extend("Saved verified evidence note\n" + item for item in st.session_state.bidforge_evidence)

        tender_text = "\n\n".join(tender_parts)
        if not tender_text.strip():
            st.error("No tender text could be extracted. Paste text or use a text-based PDF/DOCX/public webpage.")
        else:
            with st.expander("Preview extracted sources (check this before relying on the draft)", expanded=True):
                st.markdown("**Tender text**")
                st.text(tender_text[:20000])
                st.markdown("**Company evidence**")
                st.text("\n\n".join(evidence_parts)[:12000] or "No company evidence extracted.")
                for warning in source_notes:
                    st.warning(warning)

            evidence_text = "\n\n".join(evidence_parts) or "[None provided]"
            warning_text = "\n".join(source_notes) or "No extraction warnings."
            materials = f"""TENDER SOURCE TEXT:\n{tender_text}

VERIFIED COMPANY FACTS PROVIDED BY USER:\n{company_facts or '[Not provided]'}

PRICING INPUTS:\n{pricing_facts or '[Not provided; do not estimate prices]'}

REQUIRED TEMPLATE / FORMAT / LIMITS:\n{format_facts or '[Not provided]'}

COMPANY EVIDENCE AND SOURCES:\n{evidence_text}

SOURCE EXTRACTION NOTES:\n{warning_text}
"""
            with st.spinner("BidForge is preparing the selected sections…"):
                try:
                    answer = draft_response(api_key, materials, get_memory(), selected_sections)
                    st.session_state.bidforge_messages.append({"answer": answer, "sections": selected_sections})
                    st.session_state.bidforge_compliance = extract_compliance_table(answer)
                    add_to_memory("A response draft was prepared. Verify all claims and placeholders against original source documents.")
                except Exception as error:
                    st.error(f"Could not contact Groq or run the agent: {error}")

if st.session_state.bidforge_compliance is not None and not st.session_state.bidforge_compliance.empty:
    st.subheader("Editable compliance register")
    st.caption("Edit statuses, action owners, and next actions. Allowed statuses: Have it / Need to prepare / Missing info.")
    edited = st.data_editor(st.session_state.bidforge_compliance, num_rows="dynamic", use_container_width=True, key="compliance_editor")
    st.session_state.bidforge_compliance = edited
    st.download_button("Download compliance register as CSV", edited.to_csv(index=False), file_name="bidforge_compliance.csv", mime="text/csv")

for index, message in enumerate(reversed(st.session_state.bidforge_messages)):
    st.divider()
    st.subheader("Draft response package")
    st.markdown(message["answer"])
    one, two, three = st.columns(3)
    with one:
        st.download_button("Download Markdown", message["answer"], file_name=f"bidforge_response_{index + 1}.md", mime="text/markdown", key=f"md_{index}")
    with two:
        try:
            docx_bytes = to_docx(message["answer"])
            st.download_button("Download DOCX", docx_bytes, file_name=f"bidforge_response_{index + 1}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{index}")
        except Exception as error:
            st.error(f"DOCX export unavailable: {error}")
    with three:
        try:
            pdf_bytes = to_pdf(message["answer"])
            st.download_button("Download PDF", pdf_bytes, file_name=f"bidforge_response_{index + 1}.pdf", mime="application/pdf", key=f"pdf_{index}")
        except Exception as error:
            st.error(f"PDF export unavailable: {error}")

st.caption("Public link text and uploaded documents are sent to Groq when generating. Review extracted source previews and the final package. Verify all details before submission; AI output is not proof of compliance or legal advice.")
