# Document Q&A AI Agent

Imagine you have a private library of documents and a blind librarian named **Agent**. The books are your uploaded text files, stored in a PostgreSQL database. The librarian cannot read the books directly, but is equipped with **Skills (Tools)**: they can search the catalog of files, perform semantic page-by-page index searches (RAG vector retrieval via Ollama), or read a short booklet in full.

When you ask a question, the librarian doesn't just guess. They reason step-by-step:
> *"First, let me list the documents. Ah, the user is asking about hotel data. Let me search the hotel document for relevant paragraphs. I found 3 matching chunks. Now, based only on these paragraphs, here is the answer."*

This repository is that librarian: a lightweight FastAPI service powered by a reasoning LLM Agent that dynamically queries and reads your local documents to answer questions with transparency (showing its thought traces) and trust (highlighting exact sources).

---

## The Agent's Skills

* **Document Management:** Standard REST APIs (`POST /documents/`, `GET /documents/`, `DELETE /documents/`) to upload and index files.
* **Conversational Agent (`POST /agent/query`):** A unified chat endpoint driven by the Agent's reasoning loop.
  * **Real-time SSE Streaming:** Returns a `text/event-stream` using Server-Sent Events (SSE), allowing the client to consume token chunks and reasoning logs in real-time.
  * **Short-Term Memory:** Accepts `chat_history` to maintain context across follow-up questions.
  * **Scope Selection:** Pass `document_id` to focus the search on a specific file, or omit it for a global cross-document search.
  * **Dynamic UI Progress Checklist:** A Devin-style dynamic checklist showing exactly what files are being scanned or read, powered by a pure CSS spinner.
  * **Interactive Thought Logs:** A collapsible reasoning accordion that opens while the Agent is thinking and automatically collapses when the final answer starts typing out.

---

## Stream Event Schema

The stream emits standard SSE events in the following formats:
- **`event: thought`**: Emitted at the end of each reasoning loop. The `data` payload is a JSON representation of `ThoughtStep` containing loop index, token usage, tool metadata, and arguments.
- **`event: answer`**: Emitted chunk-by-chunk when generating the final text response. The `data` is a JSON object `{"text": "chunk"}`.
- **`event: done`**: Emitted once execution is complete, providing a final status.

---

## Quick Start

### 1. Run the Database
Launch the PostgreSQL database with `pgvector` extension:
```bash
docker compose up -d db
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/docqa
OLLAMA_BASE_URL=http://localhost:11434
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Application
Install dependencies and start the FastAPI server:
```bash
uv sync
uv run uvicorn app.main:app --reload
```

### 4. Open the Dashboard
Access the premium conversational UI directly in your browser:
```text
http://localhost:8000/ui
```
Drag-and-drop your `.txt` files in the sidebar and start chatting with the Agent!
