import os
import sys

import streamlit as st

if sys.version_info >= (3, 14):
    st.error(
        "This app's CrewAI/ChromaDB dependency stack is not compatible with Python 3.14. "
        "Redeploy it using Python 3.12 in Streamlit Community Cloud's Advanced settings."
    )
    st.stop()

from bidforge.agent import draft_response
from bidforge.document_reader import read_uploaded_file
from bidforge.memory import add_to_memory, get_memory, reset_memory


st.set_page_config(page_title="BidForge AI", page_icon="📑", layout="wide")
st.title("📑 BidForge AI")
st.write("Your tender response assistant. It works from the documents and facts you provide.")

# This memory is for this browser session only. It is not permanent company storage.
if "bidforge_memory" not in st.session_state:
    st.session_state.bidforge_memory = []
if "bidforge_messages" not in st.session_state:
    st.session_state.bidforge_messages = []

with st.sidebar:
    st.header("Tender document")
    tender_upload = st.file_uploader("Upload tender/RFP", type=["pdf", "docx", "txt", "md"])
    tender_paste = st.text_area("Or paste tender text", height=150)

    st.header("Company evidence")
    company_uploads = st.file_uploader(
        "Upload profile, CVs, certificates, references, templates",
        type=["pdf", "docx", "txt", "md", "csv"],
        accept_multiple_files=True,
    )

    with st.expander("Add company and pricing details"):
        company_facts = st.text_area(
            "Company information",
            placeholder="Name, registration, certifications, past projects, financial standing, team…",
            height=150,
        )
        pricing_facts = st.text_area(
            "Pricing information (optional)",
            placeholder="Rates, quantities, taxes, currency, cost estimates…",
            height=100,
        )
        format_facts = st.text_area(
            "Tender format/page requirements (optional)",
            placeholder="Required headings, forms, page limits, format…",
            height=100,
        )

    st.header("Session memory")
    st.caption(f"{len(get_memory())} saved note(s) in this browser session.")
    with st.expander("Add a note for this session"):
        note = st.text_area("Memory note", placeholder="Example: Our bid currency is PKR.")
        if st.button("Save note"):
            if note.strip():
                add_to_memory(note.strip())
                st.success("Saved for this session.")
                st.rerun()
    if st.button("Clear session memory"):
        reset_memory()
        st.rerun()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

st.info("Groq model: openai/gpt-oss-120b · Add GROQ_API_KEY in Streamlit Cloud → App settings → Secrets.")

if st.button("Create response package", type="primary", use_container_width=True):
    if not api_key:
        st.error("GROQ_API_KEY is missing. Add it to Streamlit Cloud Secrets, then restart the app.")
    elif not tender_upload and not tender_paste.strip():
        st.error("Upload or paste the tender/RFP first.")
    else:
        with st.spinner("Reading documents and preparing a draft…"):
            tender_text = tender_paste.strip()
            evidence = []
            if tender_upload:
                parsed, warning = read_uploaded_file(tender_upload)
                tender_text = (tender_text + "\n\n" if tender_text else "") + parsed
                if warning:
                    st.warning(warning)
            for uploaded in company_uploads or []:
                parsed, warning = read_uploaded_file(uploaded)
                if parsed.strip():
                    evidence.append(f"### {uploaded.name}\n{parsed}")
                if warning:
                    st.warning(warning)

            request = f"""TENDER TEXT:\n{tender_text}

COMPANY INFORMATION PROVIDED BY USER:\n{company_facts or '[Not provided]'}

PRICING INPUTS:\n{pricing_facts or '[Not provided; use a blank fill-in table]'}

FORMAT / TEMPLATE INSTRUCTIONS:\n{format_facts or '[Not provided]'}

SUPPORTING DOCUMENTS:\n{chr(10).join(evidence) if evidence else '[None provided]'}
"""
            try:
                answer = draft_response(api_key, request, get_memory())
                st.session_state.bidforge_messages.append({"question": "Create response package", "answer": answer})
                add_to_memory("A tender response draft was generated. The user can review its placeholders and add follow-up session notes.")
            except Exception as error:
                st.error(f"Could not contact Groq or run the agent: {error}")

for message in reversed(st.session_state.bidforge_messages):
    st.divider()
    st.markdown(message["answer"])
    st.download_button(
        "Download this draft as Markdown",
        message["answer"],
        file_name="bidforge_response.md",
        mime="text/markdown",
        key=f"download_{st.session_state.bidforge_messages.index(message)}",
    )

st.caption("Drafts require human verification against the complete tender. Do not rely on AI output as proof of compliance or legal advice.")
