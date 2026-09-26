# BidForge AI

BidForge AI is a single-agent tender response drafting app built with Streamlit, CrewAI, and Groq's `openai/gpt-oss-120b` model.

The workspace is organized into Dashboard, Tender Analysis, Company Evidence, Bid Builder, Compliance, and Documents tabs. Its light enterprise styling distinguishes source evidence, user input, AI drafts, and items that still need review.

## Included features

- Upload a tender, paste its text, or import a public tender webpage/direct PDF link.
- Add public company profile links, uploaded company evidence, templates, and verified company facts.
- Preview extracted tender/company text before generation.
- Select which sections to generate: tender analysis, compliance checklist, scope/clarifications, technical proposal, financial structure, supporting documents, readiness report, and quality review.
- Edit the generated compliance table and download it as CSV.
- Save company evidence notes for the current browser session and clear them when finished.
- OCR scanned PDFs (first 30 pages), subject to OCR accuracy; verify the extracted text.
- Download the response as Markdown, DOCX, or PDF.
- Edit generated response drafts in the Documents tab, save edits for the current browser session, restore the original AI text, and download the edited version.
- See a formatted preview alongside the draft editor; DOCX/PDF exports render Markdown tables as aligned tables.
- PDF and DOCX source text includes page or paragraph markers when available; compliance rows request tender excerpts and company evidence references, with a per-requirement source inspector in the Compliance tab.
- Tool-assisted tender requirement scan and arithmetic check for complete supplied price rows.
- Long-tender workflow: tenders over 10,000 characters are analyzed in source-marked sections, with visible progress and an explicit warning if the section limit leaves content unreviewed.
- Optional on-demand evidence and claim audit in Documents compares draft statements with the tender/company material saved for that draft. It consumes Groq tokens only when requested and must be checked by a person.
- Rate-limit handling: request context is compacted, output length is bounded, and the app honors Groq's suggested wait while progressively lowering the response token budget on TPM retries.

## Repository structure

```text
bidforge-ai/
├── app.py
├── requirements.txt
├── packages.txt
├── .streamlit/
│   └── config.toml
├── assets/
│   └── bidforge-logo.png
└── bidforge/
    ├── __init__.py
    ├── agent.py
    ├── document_reader.py
    ├── exports.py
    ├── memory.py
    ├── tools.py
    └── web_reader.py
```

## GitHub and Streamlit Cloud setup

1. Create a GitHub repository called `bidforge-ai`.
2. In GitHub, choose **Add file → Create new file**. Add each path above, pasting in the matching file from this project. Enter names such as `bidforge/agent.py` to create files in the `bidforge` folder. Upload `assets/bidforge-logo.png` with **Add file → Upload files** so the logo stays a binary PNG. Commit each file. Keep `app.py`, `requirements.txt`, and `packages.txt` at the repository root.
3. Create an API key in [Groq Console](https://console.groq.com/keys). Keep the key secret and do not put it in the repository.
4. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and create an app from the GitHub repository. Choose the `main` branch and `app.py` entry point.
5. In **Advanced settings**, choose **Python 3.12**. If the existing deployment uses Python 3.14, save its Groq key and delete/recreate the Streamlit app to choose Python 3.12; the GitHub repository itself stays intact.
6. Add the following in the deployment **Secrets** field:

   ```toml
   GROQ_API_KEY = "your-real-groq-api-key"
   ```

7. Deploy. Streamlit installs Python dependencies from `requirements.txt` and system packages from `packages.txt`. New commits to the selected GitHub branch trigger redeployment.

## Public link import

The app fetches publicly accessible HTTP(S) pages and direct PDF links, up to 5 MB per link. It does not sign in to sites, follow redirects, or access private/internal network addresses. If the site blocks automated requests, paste the relevant text or upload the file. Review the extracted preview before generating a draft. Webpage content is reference material, not proof that company claims are valid.

## Memory and privacy

Saved evidence and memory are limited to the current Streamlit browser session. They are cleared when the session ends or the app restarts. For long-term or multi-user storage, add a managed database and authentication before storing confidential data. Uploaded text and imported link text are sent to Groq when you generate a response. Use only sources your organization permits you to process this way.

## Important safeguards

- The agent must not invent credentials, references, personnel, dates, or prices. Missing bidder inputs should remain `[TO BE PROVIDED]`.
- Public company pages may be outdated or promotional. Verify all extracted claims and upload authoritative supporting documents.
- OCR can misread scanned pages; check the extracted source preview and original documents.
- DOCX/PDF exports provide a basic text layout. They do not reproduce an issuer's exact template design or guarantee page limits. Review and format against the actual tender requirements before submission.
- Bid bonds, original/certified/notarized certificates, and signed declarations must be obtained from their issuers. The app can checklist them only.
- Legal/contractual clauses are flagged for human/legal review; the app does not provide legal advice.
- Output is a draft, not a guarantee of compliance.
