# BidForge AI

Beginner-friendly tender response assistant built with **Streamlit + CrewAI + Groq**. One CrewAI agent uses two tools to scan tender requirements and check arithmetic for explicitly supplied prices. It uses Groq's `openai/gpt-oss-120b` model.

## Project files

```text
bidforge-ai/
├── app.py
├── requirements.txt
└── bidforge/
    ├── __init__.py
    ├── agent.py
    ├── document_reader.py
    ├── memory.py
    └── tools.py
```

## Step 1: Create the GitHub repository

1. Sign in at [GitHub](https://github.com/) and choose **New repository**.
2. Name it `bidforge-ai`. Choose **Public** for the simplest Streamlit connection, or Private if you prefer; Streamlit must be authorized to access a private repository.
3. Choose **Create repository**.

## Step 2: Add files using GitHub's website

You do not need to install anything on your computer. In the new repository, use **Add file → Create new file** for each file below. Enter the path in the filename box; GitHub creates the folder when the path includes `/`.

Create these paths and paste in the matching code from this project:

1. `app.py`
2. `requirements.txt`
3. `bidforge/__init__.py`
4. `bidforge/agent.py`
5. `bidforge/document_reader.py`
6. `bidforge/memory.py`
7. `bidforge/tools.py`

For each file, select **Commit changes**. You may also upload the files with **Add file → Upload files** if you have them available on your device. Keep the folder paths shown above.

## Step 3: Get a Groq API key

1. Sign in to [Groq Console](https://console.groq.com/keys).
2. Create an API key and copy it somewhere safe. Do not put it into a Python file or commit it to GitHub.

## Step 4: Deploy on Streamlit Community Cloud

1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
2. Authorize Streamlit to access the GitHub repository. For a private repository, grant the requested private-repository access.
3. Choose **Create app**, then select your `bidforge-ai` repository, the `main` branch, and `app.py` as the app file.
4. Open **Advanced settings** and select **Python 3.12**. This project uses CrewAI, which imports ChromaDB; the Python 3.14 / Pydantic v1 compatibility combination can fail during import.
5. Add this secret, replacing the example with your actual Groq key:

   ```toml
   GROQ_API_KEY = "paste-your-real-key-here"
   ```

6. Click **Deploy**. Streamlit installs packages from `requirements.txt` and starts the app. Future commits to the selected GitHub branch trigger app updates.

### If the existing app already uses Python 3.14

Streamlit Community Cloud does not let you change an app's Python version after deployment. Save the Groq secret, delete the **deployed app** from Streamlit (this does not delete your GitHub repository), then create/deploy the app again and select Python 3.12 in **Advanced settings**. Re-enter the `GROQ_API_KEY` secret when prompted. See [Streamlit's Python version instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python).

## Step 5: Use the app

1. Upload a text-based PDF, DOCX, TXT, or Markdown tender, or paste the tender text.
2. Add company facts, supporting documents, and any bid pricing or formatting instructions.
3. Click **Create response package** and review the generated checklist and draft.
4. Download the response as Markdown. Verify all details against the original tender before submission.

## Tools included

- **Tender requirement scanner:** finds lines mentioning common tender topics such as submission deadlines, eligibility, evaluation, bid security, and legal terms. It only searches the text you provide; it does not browse the web.
- **Pricing arithmetic checker:** multiplies supplied quantity and unit-price pairs. It will not supply missing prices, taxes, or fees.

## Memory and privacy

This starter has short-term memory for the current Streamlit browser session: it can use notes you save during that session and you can clear them in the sidebar. Conversation continuity resets when the session ends, the app restarts, or you open a new session. This avoids pretending that Streamlit's temporary app filesystem is a permanent database. The starter does **not** keep company facts between visits. For cross-session, multi-user memory, add a managed database (for example, Supabase) with user authentication and access controls before storing confidential tender or company data.

The app sends the text you submit to Groq to generate the response. Do not upload sensitive documents unless your organization approves that processing.

## Important limitations

- Never treat generated output as guaranteed compliant. Have a person review every requirement and response.
- Missing company facts and prices should remain `[TO BE PROVIDED]`; the model must not invent qualifications or evidence.
- The app flags legal clauses for human/legal review and does not provide legal advice.
- Scanned PDFs with no selectable text may not work. Convert them to searchable PDF or paste the relevant text.
- Bid bonds, signed declarations, original/certified certificates, and notarized documents must be obtained from their proper issuers; the app only lists them.
- `GROQ_API_KEY` must remain in Streamlit Secrets. If a key is ever committed to GitHub, revoke it and create a new one.
