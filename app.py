import os
import re
import sys

import pandas as pd
import streamlit as st

st.set_page_config(page_title="BidForge AI | Tender Workspace", page_icon="📑", layout="wide")

if sys.version_info >= (3, 14):
    st.error("Please redeploy BidForge AI using Python 3.12 in Streamlit Community Cloud.")
    st.stop()

from bidforge.agent import draft_response
from bidforge.document_reader import read_uploaded_file
from bidforge.exports import to_docx, to_pdf
from bidforge.memory import add_to_memory, get_memory, reset_memory
from bidforge.web_reader import fetch_public_text


st.markdown(
    """
    <style>
      :root { --bf-blue:#2563eb; --bf-blue-dark:#1d4ed8; --bf-teal:#0f766e; --bf-ink:#111827; --bf-muted:#64748b; --bf-line:#e2e8f0; --bf-bg:#f6f8fc; }
      .stApp { background: radial-gradient(ellipse at 8% 0%, rgba(37,99,235,.055), transparent 34%), radial-gradient(ellipse at 92% 9%, rgba(15,118,110,.045), transparent 26%), #f7f9fc; color:var(--bf-ink); }
      html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { color:#111827 !important; color-scheme:light !important; }
      .block-container { max-width: 1440px; padding-top: 1.1rem; padding-bottom: 3rem; }
      [data-testid="stHeader"] { background:rgba(247,249,252,.85); }
      [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--bf-line); }
      [data-testid="stTabs"] button { font-weight:600; color:#475569 !important; opacity:1 !important; }
      [data-testid="stTabs"] button p, [data-testid="stTabs"] button span { color:#475569 !important; opacity:1 !important; }
      [data-testid="stTabs"] button[aria-selected="true"], [data-testid="stTabs"] button[aria-selected="true"] p, [data-testid="stTabs"] button[aria-selected="true"] span { color:#1d4ed8 !important; }
      label, label p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p { color:#334155 !important; opacity:1 !important; }
      [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] p { color:#526174; }
      input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea { background:#fff !important; color:#111827 !important; -webkit-text-fill-color:#111827 !important; border-color:#cbd5e1 !important; opacity:1 !important; }
      input::placeholder, textarea::placeholder { color:#94a3b8 !important; -webkit-text-fill-color:#94a3b8 !important; opacity:1 !important; }
      [data-baseweb="select"] > div { background:#fff !important; color:#111827 !important; border-color:#cbd5e1 !important; }
      [data-testid="stFileUploaderDropzone"] { background:#fff !important; color:#334155 !important; border-color:#b9c8dc !important; }
      [data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploaderDropzone"] button { color:#334155 !important; opacity:1 !important; }
      [data-testid="stFileUploaderDropzone"] button { background:#fff !important; border:1px solid #cbd5e1 !important; }
      [data-testid="stFileUploaderDropzone"] small { color:#64748b !important; }
      [data-testid="stDataEditor"] { color:#111827 !important; }
      .bf-topbar { display:flex; align-items:center; justify-content:space-between; padding:.65rem 0 1rem; border-bottom:1px solid var(--bf-line); margin-bottom:1.35rem; }
      .bf-brand { display:flex; align-items:center; gap:.7rem; color:var(--bf-ink); font-size:1.13rem; font-weight:750; letter-spacing:-.02em; }
      .bf-mark { display:grid; place-items:center; width:38px; height:38px; border-radius:11px; background:#eaf1ff; color:var(--bf-blue-dark); border:1px solid #d7e4ff; font-size:.8rem; font-weight:800; }
      .bf-state { color:#475569; background:#fff; border:1px solid var(--bf-line); padding:.4rem .7rem; border-radius:999px; font-size:.78rem; }
      .bf-hero { background:linear-gradient(110deg,#fff 0%,#f5f8ff 70%,#f2fbfa 100%); border:1px solid #dfe7f2; border-radius:18px; padding:1.65rem 1.8rem; box-shadow:0 5px 18px rgba(15,23,42,.035); }
      .bf-eyebrow { color:var(--bf-blue-dark); text-transform:uppercase; letter-spacing:.09em; font-weight:750; font-size:.72rem; }
      .bf-hero h1 { margin:.35rem 0 .45rem; font-size:2.05rem; line-height:1.2; letter-spacing:-.04em; color:var(--bf-ink); }
      .bf-hero p { color:#526174; max-width:760px; margin:0; font-size:1rem; }
      .bf-pills { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1.05rem; }
      .bf-pill { padding:.32rem .58rem; border-radius:7px; background:#fff; color:#475569; border:1px solid var(--bf-line); font-size:.74rem; font-weight:650; }
      .bf-card { background:#fff; border:1px solid var(--bf-line); border-radius:14px; padding:1rem 1.05rem; box-shadow:0 3px 12px rgba(15,23,42,.025); min-height:92px; }
      .bf-card-label { color:#64748b; font-size:.77rem; font-weight:650; }
      .bf-card-value { color:#111827; font-size:1.4rem; font-weight:750; margin-top:.28rem; letter-spacing:-.03em; }
      .bf-card-note { color:#64748b; font-size:.75rem; margin-top:.15rem; }
      .bf-section { color:#111827; font-weight:750; letter-spacing:-.02em; font-size:1.15rem; margin:.2rem 0 .25rem; }
      .bf-sub { color:#64748b; font-size:.88rem; margin-bottom:.7rem; }
      .bf-stage { text-align:center; background:#fff; border:1px solid var(--bf-line); border-radius:12px; padding:.8rem .35rem; color:#334155; font-size:.78rem; font-weight:650; }
      .bf-stage strong { display:block; color:var(--bf-blue-dark); font-size:.72rem; margin-bottom:.25rem; }
      .bf-review { background:#fff8e9; border:1px solid #f3d8a5; color:#7c4a03; border-radius:12px; padding:.85rem 1rem; font-size:.87rem; margin:1rem 0; }
      .bf-source { display:inline-block; padding:.22rem .5rem; border-radius:6px; background:#eaf2ff; color:#1d4ed8; font-weight:650; font-size:.72rem; }
      .bf-ai { display:inline-block; padding:.22rem .5rem; border-radius:6px; background:#f1eaff; color:#6d28d9; font-weight:650; font-size:.72rem; }
      .bf-user { display:inline-block; padding:.22rem .5rem; border-radius:6px; background:#f1f5f9; color:#475569; font-weight:650; font-size:.72rem; }
      .bf-review-badge { display:inline-block; padding:.22rem .5rem; border-radius:6px; background:#fff2da; color:#a35b00; font-weight:650; font-size:.72rem; }
      div[data-testid="stButton"] button[kind="primary"] { background:var(--bf-blue); border-color:var(--bf-blue); border-radius:9px; font-weight:700; }
      div[data-testid="stButton"] button { border-radius:9px; }
      div[data-testid="stFileUploader"] section { background:#fff !important; color:#334155 !important; border:1px dashed #b9c8dc; border-radius:12px; }
      [data-testid="stDataEditor"] { border:1px solid var(--bf-line); border-radius:10px; overflow:hidden; }
      @media(max-width:760px) { .bf-hero h1 {font-size:1.6rem;} .block-container {padding-left:1rem;padding-right:1rem;} }
    </style>
    <div class="bf-topbar"><div class="bf-brand"><div class="bf-mark">BF</div><span>BidForge AI</span></div><div class="bf-state">● Session active &nbsp;·&nbsp; Groq / GPT-OSS-120B</div></div>
    """,
    unsafe_allow_html=True,
)

for key, default in {
    "bidforge_memory": [], "bidforge_messages": [], "bidforge_evidence": [],
    "bidforge_compliance": None, "bidforge_pricing": pd.DataFrame(columns=["Resource", "Unit", "Rate", "Currency"]),
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def extract_compliance_table(markdown: str) -> pd.DataFrame:
    rows, in_table = [], False
    for line in markdown.splitlines():
        if line.strip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            if not in_table:
                in_table = True
                continue
            if len(cells) >= 4:
                rows.append((cells + [""] * 5)[:5])
        elif in_table:
            break
    return pd.DataFrame(rows, columns=["Requirement", "Source", "Status", "Evidence / next action", "Owner"])


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(f'<div class="bf-card"><div class="bf-card-label">{label}</div><div class="bf-card-value">{value}</div><div class="bf-card-note">{note}</div></div>', unsafe_allow_html=True)


def compact_tender_excerpt(text: str, limit: int = 7600) -> str:
    """Keep an initial overview, requirement-bearing lines, and the closing portion."""
    if len(text) <= limit:
        return text
    terms = ("deadline", "closing date", "submission", "eligibility", "evaluation", "scope", "deliverable", "mandatory", "bid security", "financial", "pricing", "technical", "clarification", "page limit", "penalty", "liability", "contract", "warranty", "key date")
    selected = [text[:1700], "[Tender source excerpted to fit the model request budget]"]
    used = sum(map(len, selected))
    for line in text.splitlines():
        if any(term in line.lower() for term in terms):
            item = line.strip()[:260]
            if item and item not in selected and used + len(item) + 1 < limit - 1200:
                selected.append(item)
                used += len(item) + 1
    selected.append("[End of tender excerpt]\n" + text[-1000:])
    return "\n".join(selected)


st.markdown(
    '<div class="bf-hero"><div class="bf-eyebrow">Tender response workspace</div><h1>Turn complex tenders into structured bid drafts.</h1><p>Upload a tender, provide verified company evidence, and prepare a response with visible compliance gaps and review actions.</p><div class="bf-pills"><span class="bf-pill">Source-grounded</span><span class="bf-pill">Compliance-focused</span><span class="bf-pill">Human-reviewed</span></div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="bf-review"><strong>Human review required</strong> &nbsp; BidForge creates drafts from supplied information. Verify requirements, evidence, prices, deadlines, and legal conditions against the original tender before submission.</div>', unsafe_allow_html=True)

tabs = st.tabs(["Dashboard", "Tender Analysis", "Company Evidence", "Bid Builder", "Compliance", "Documents"])

with tabs[0]:
    st.markdown('<div class="bf-section">Tender workflow</div><div class="bf-sub">A clear path from tender intake to a reviewed submission package.</div>', unsafe_allow_html=True)
    stage_cols = st.columns(8)
    stages = ["Tender", "Analyze", "Scope", "Compliance", "Technical", "Financial", "Review", "Package"]
    for idx, (col, stage) in enumerate(zip(stage_cols, stages), start=1):
        with col:
            st.markdown(f'<div class="bf-stage"><strong>{idx:02}</strong>{stage}</div>', unsafe_allow_html=True)
    st.write("")
    card_cols = st.columns(4)
    latest = st.session_state.bidforge_messages[-1]["answer"] if st.session_state.bidforge_messages else ""
    with card_cols[0]:
        metric_card("Tender source", "Ready" if st.session_state.get("source_tender_text") else "Not added", "Upload, paste, or use a public link")
    with card_cols[1]:
        metric_card("Company evidence", str(st.session_state.get("source_evidence_count", 0)), "Uploaded or saved evidence items")
    with card_cols[2]:
        count = len(st.session_state.bidforge_compliance) if isinstance(st.session_state.bidforge_compliance, pd.DataFrame) else 0
        metric_card("Compliance items", str(count), "Extracted into the editable register")
    with card_cols[3]:
        metric_card("Draft package", "Available" if latest else "Not generated", "Draft output requires review")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="bf-source">SOURCE EVIDENCE</span> &nbsp; <span class="bf-ai">AI DRAFT</span> &nbsp; <span class="bf-user">USER INPUT</span> &nbsp; <span class="bf-review-badge">NEEDS REVIEW</span>', unsafe_allow_html=True)
    st.caption("Use the tabs above to add tender sources, company evidence, prepare sections, and review the outputs.")

with tabs[1]:
    st.markdown('<div class="bf-section">Tender Analysis</div><div class="bf-sub">Add the source document or a public link. Extracted text is previewed before the agent uses it.</div>', unsafe_allow_html=True)
    lcol, rcol = st.columns([1.1, .9])
    with lcol:
        tender_url = st.text_input("Public tender webpage or direct PDF link", placeholder="https://…", key="tender_url")
        tender_upload = st.file_uploader("Upload an RFP, RFT, RFQ, EOI, or tender", type=["pdf", "docx", "txt", "md", "csv"], key="tender_upload")
        pasted_tender = st.text_area("Or paste tender text", height=145, key="tender_paste")
        st.caption("Maximum upload size: 200 MB per file.")
        if tender_upload:
            st.success(f"{tender_upload.name} · {tender_upload.size / (1024 * 1024):.2f} MB · ready to extract")
    with rcol:
        st.markdown('<div class="bf-card"><div class="bf-card-label">Supported sources</div><div class="bf-card-value" style="font-size:1.05rem">PDF · DOCX · TXT · MD · CSV</div><div class="bf-card-note">Public HTTP(S) page or direct PDF link also supported · 5 MB per link</div></div>', unsafe_allow_html=True)
        st.caption("Scanned PDFs use OCR when available. Review OCR text for reading errors. Links requiring sign-in or redirecting are not fetched.")
    tender_preview_parts, tender_warnings = [], []
    if pasted_tender.strip():
        tender_preview_parts.append("Pasted tender text\n" + pasted_tender.strip())
    if tender_upload:
        parsed, warning = read_uploaded_file(tender_upload)
        if parsed.strip():
            tender_preview_parts.append(f"Uploaded tender: {tender_upload.name}\n{parsed}")
        if warning:
            tender_warnings.append(warning)
    if tender_url.strip():
        try:
            parsed, warning = fetch_public_text(tender_url.strip())
            if parsed.strip():
                tender_preview_parts.append("Linked tender source\n" + parsed)
            if warning:
                tender_warnings.append(warning)
        except Exception as error:
            tender_warnings.append(f"Tender link could not be read: {error}")
    tender_text = "\n\n".join(tender_preview_parts)
    st.session_state.source_tender_text = tender_text
    with st.expander("Preview extracted tender source", expanded=bool(tender_text)):
        st.markdown('<span class="bf-source">SOURCE EVIDENCE</span>', unsafe_allow_html=True)
        st.text(tender_text[:30000] if tender_text else "Add a tender source to preview its extracted text.")
        for warning in tender_warnings:
            st.warning(warning)

with tabs[2]:
    st.markdown('<div class="bf-section">Company Evidence</div><div class="bf-sub">Provide verified company information and supporting documents. BidForge will not treat missing claims as established facts.</div>', unsafe_allow_html=True)
    company_urls = st.text_area("Public company profile links (one per line)", height=85, placeholder="https://company.example/about\nhttps://company.example/projects", key="company_urls")
    company_files = st.file_uploader("Company profile, CVs, certificates, references, case studies, previous bids, templates", type=["pdf", "docx", "txt", "md", "csv"], accept_multiple_files=True, key="company_files")
    if company_files:
        for file in company_files:
            st.caption(f"Ready · {file.name} · {file.size / (1024 * 1024):.2f} MB")
    evidence_cols = st.columns(4)
    categories = [("Company profile", ["profile", "company", "about"]), ("CVs & personnel", ["cv", "resume", "personnel"]), ("Certificates", ["cert", "iso", "license"]), ("Projects & references", ["project", "reference", "case", "client"])]
    for col, (name, keys) in zip(evidence_cols, categories):
        count = sum(1 for f in (company_files or []) if any(k in f.name.lower() for k in keys))
        with col:
            metric_card(name, str(count), "Uploaded documents detected by filename")
    evidence_parts, evidence_warnings = [], []
    with st.expander("Company, pricing, and tender format details", expanded=True):
        company_tab, pricing_tab, format_tab = st.tabs(["Company information", "Pricing", "Tender format"])
        with company_tab:
            company_facts = st.text_area("Verified organization, capabilities, registrations, certifications, projects, personnel", height=160, placeholder="Only include details you can substantiate.", key="company_facts")
        with pricing_tab:
            st.caption("Optional pricing inputs. Rates and costs remain user-provided; all AI-prepared pricing needs approval.")
            pricing_csv = st.file_uploader("Import pricing CSV (optional)", type=["csv"], key="pricing_csv")
            if pricing_csv:
                try:
                    st.session_state.bidforge_pricing = pd.read_csv(pricing_csv)
                except Exception as error:
                    st.warning(f"Could not read pricing CSV: {error}")
            pricing_table = st.data_editor(st.session_state.bidforge_pricing, num_rows="dynamic", use_container_width=True, key="pricing_editor")
            st.session_state.bidforge_pricing = pricing_table
            pricing_text = st.text_area("Additional pricing assumptions, currency, tax or rate details", height=90, key="pricing_text")
            if not pricing_table.empty:
                st.download_button("Export pricing CSV", pricing_table.to_csv(index=False), file_name="bidforge_pricing.csv", mime="text/csv")
        with format_tab:
            format_facts = st.text_area("Required headings, issuer templates, page limits, file format, packaging", height=130, key="format_facts")
            st.caption("Uploaded templates are read as source text. DOCX/PDF exports use a basic layout and do not reproduce the issuer's exact visual template.")
    for item in company_files or []:
        parsed, warning = read_uploaded_file(item)
        if parsed.strip():
            evidence_parts.append(f"Uploaded source: {item.name}\n{parsed}")
        if warning:
            evidence_warnings.append(warning)
    for url in [line.strip() for line in company_urls.splitlines() if line.strip()]:
        try:
            parsed, warning = fetch_public_text(url)
            if parsed.strip():
                evidence_parts.append(f"Company link source\n{parsed}")
            if warning:
                evidence_warnings.append(f"Company link {url}: {warning}")
        except Exception as error:
            evidence_warnings.append(f"Company link {url} could not be read: {error}")
    st.session_state.source_evidence_count = len(company_files or []) + len([line for line in company_urls.splitlines() if line.strip()]) + len(st.session_state.bidforge_evidence)
    with st.expander("Evidence library and session memory"):
        st.caption(f"Session evidence: {len(st.session_state.bidforge_evidence)} saved note(s) · Session memory: {len(get_memory())} note(s). These are cleared when the session ends.")
        reusable = st.text_area("Add a verified company fact to this session's evidence library", placeholder="Example: ISO certificate number, expiry date, and certificate name", key="evidence_note")
        e1, e2 = st.columns(2)
        with e1:
            if st.button("Save evidence note", key="save_evidence") and reusable.strip():
                st.session_state.bidforge_evidence.append(reusable.strip())
                st.rerun()
        with e2:
            if st.button("Clear session memory and evidence", key="clear_evidence"):
                reset_memory()
                st.session_state.bidforge_evidence = []
                st.rerun()
        for i, item in enumerate(st.session_state.bidforge_evidence, start=1):
            st.markdown(f"**Evidence note {i}** · {item}")
        note = st.text_input("Session note for BidForge", placeholder="Example: Use PKR as bid currency", key="memory_note")
        if st.button("Add session note", key="add_memory") and note.strip():
            add_to_memory(note.strip())
            st.rerun()
    with st.expander("Preview extracted company evidence"):
        st.markdown('<span class="bf-source">SOURCE EVIDENCE</span>', unsafe_allow_html=True)
        st.text("\n\n".join(evidence_parts)[:20000] or "No uploaded or linked company source text yet.")
        for warning in evidence_warnings:
            st.warning(warning)

with tabs[3]:
    st.markdown('<div class="bf-section">Bid Builder</div><div class="bf-sub">Choose the response sections to draft from the tender and evidence provided.</div>', unsafe_allow_html=True)
    output_options = ["Tender analysis and facts", "Compliance checklist", "Scope of work and clarification questions", "Technical proposal", "Financial bid structure", "Supporting documents checklist", "Final readiness review", "Proposal quality review"]
    chosen_sections = st.multiselect("Select sections", output_options, default=output_options, key="output_sections")
    stage_progress = 1.0 if st.session_state.bidforge_messages else 0.0
    st.markdown("**Preparation progress**")
    st.progress(stage_progress, text="Draft generated — human review required" if stage_progress else "Waiting for tender and evidence")
    st.markdown("**BidForge agent workflow**")
    if st.session_state.bidforge_messages:
        st.success("Tender analyzed · Selected sections drafted · Compliance register ready for review")
    else:
        st.caption("Ready to read tender · Extract requirements · Match supplied company evidence · Draft selected sections")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        st.warning("AI service setup is incomplete. Add GROQ_API_KEY in Streamlit Cloud → App settings → Secrets.")
    if st.button("Generate response draft", type="primary", use_container_width=True, key="generate_bid"):
        if not api_key:
            st.error("AI service connection issue. Check that the Groq API key is present in Streamlit Secrets.")
        elif not chosen_sections:
            st.warning("Choose at least one section to generate.")
        elif not tender_text.strip():
            st.warning("Add a tender source in Tender Analysis first.")
        else:
            evidence_parts.extend("Saved verified evidence note\n" + item for item in st.session_state.bidforge_evidence)
            price_grid = pricing_table.to_csv(index=False)[:900] if not pricing_table.empty else ""
            compact_tender = compact_tender_excerpt(tender_text)
            materials = f"""TENDER SOURCE TEXT (selected overview and requirement-bearing excerpts):\n{compact_tender}

VERIFIED COMPANY FACTS PROVIDED BY USER:\n{company_facts[:1000] or '[Not provided]'}

PRICING INPUTS FROM EDITABLE PRICE TABLE:\n{price_grid or '[None provided]'}
ADDITIONAL PRICING INPUTS:\n{pricing_text[:600] or '[Not provided; do not estimate prices]'}

REQUIRED TEMPLATE / FORMAT / LIMITS:\n{format_facts[:500] or '[Not provided]'}

COMPANY EVIDENCE AND SOURCES:\n{chr(10).join(evidence_parts)[:2200] or '[None provided]'}

SOURCE EXTRACTION NOTES:\n{chr(10).join(tender_warnings + evidence_warnings) or 'No extraction warnings.'}
"""
            with st.spinner("Reading tender requirements and drafting selected sections… If Groq rate-limits the request, BidForge will wait and retry once."):
                try:
                    answer = draft_response(api_key, materials, get_memory(), chosen_sections)
                    st.session_state.bidforge_messages.append({"answer": answer, "sections": chosen_sections})
                    st.session_state.bidforge_compliance = extract_compliance_table(answer)
                    add_to_memory("A response draft was generated. Verify claims and all placeholders against original tender sources.")
                    st.success("Draft ready for review.")
                except Exception as error:
                    details = str(error)
                    if "RateLimitError" in details or "rate_limit_exceeded" in details:
                        st.warning("Groq is temporarily at its token-per-minute limit. BidForge waited and retried once, but the request still exceeded the current allowance. Wait briefly and try again with fewer sections selected.")
                    else:
                        st.error("AI service connection issue. BidForge could not complete this draft. Check Groq configuration and retry.")
                    with st.expander("Technical details"):
                        st.code(details)

with tabs[4]:
    st.markdown('<div class="bf-section">Compliance Matrix</div><div class="bf-sub">Trace requirements to their source and record the evidence or action needed.</div>', unsafe_allow_html=True)
    if st.session_state.bidforge_compliance is not None and not st.session_state.bidforge_compliance.empty:
        matrix = st.session_state.bidforge_compliance.copy()
        if "Mandatory" not in matrix.columns:
            matrix.insert(1, "Mandatory", "Needs review")
        if "Company evidence" not in matrix.columns:
            matrix.insert(2, "Company evidence", "[TO BE PROVIDED / verify]")
        if "Response" not in matrix.columns:
            matrix.insert(3, "Response", "[AI draft — review]")
        st.caption("AI Draft and Needs Review labels identify generated or unverified content. Use the editable fields to record human findings.")
        edited = st.data_editor(matrix, num_rows="dynamic", use_container_width=True, key="compliance_matrix")
        st.session_state.bidforge_compliance = edited
        st.download_button("Export compliance matrix (CSV)", edited.to_csv(index=False), file_name="bidforge_compliance_matrix.csv", mime="text/csv", key="matrix_csv")
        with st.expander("Source evidence and extracted tender text"):
            st.text(tender_text[:25000] or "Tender text is not available in this session.")
    else:
        st.info("Generate a draft with the Compliance checklist selected to populate the matrix.")

with tabs[5]:
    st.markdown('<div class="bf-section">Bid Documents</div><div class="bf-sub">Drafts remain unapproved until reviewed by your bid team.</div>', unsafe_allow_html=True)
    if not st.session_state.bidforge_messages:
        st.info("Generated response documents will appear here.")
    for index, message in enumerate(reversed(st.session_state.bidforge_messages), start=1):
        st.markdown(f'<div class="bf-card"><div class="bf-card-label">Response package · Draft {len(st.session_state.bidforge_messages) - index + 1}</div><div class="bf-card-value" style="font-size:1.1rem">Selected tender sections</div><div class="bf-card-note">{", ".join(message["sections"])} · <span style="color:#a35b00">Needs review</span></div></div>', unsafe_allow_html=True)
        with st.expander("Preview draft", expanded=index == 1):
            st.markdown('<span class="bf-ai">AI DRAFT</span> &nbsp; <span class="bf-review-badge">NEEDS REVIEW</span>', unsafe_allow_html=True)
            st.markdown(message["answer"])
            left, middle, right = st.columns(3)
            with left:
                st.download_button("Download Markdown", message["answer"], file_name=f"bidforge_response_{index}.md", mime="text/markdown", key=f"md_{index}")
            with middle:
                try:
                    st.download_button("Download DOCX", to_docx(message["answer"]), file_name=f"bidforge_response_{index}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{index}")
                except Exception as error:
                    st.error(f"DOCX export unavailable: {error}")
            with right:
                try:
                    st.download_button("Download PDF", to_pdf(message["answer"]), file_name=f"bidforge_response_{index}.pdf", mime="application/pdf", key=f"pdf_{index}")
                except Exception as error:
                    st.error(f"PDF export unavailable: {error}")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.caption("Source Evidence = extracted from a supplied document or public page · User Input = entered or saved by you · AI Draft = generated response content · Needs Review = verify against the original tender and authoritative evidence.")
