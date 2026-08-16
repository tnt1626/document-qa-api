# Document Q&A API

A lightweight FastAPI service for uploading text documents, chunking them, embedding the content with Ollama, storing vector data in PostgreSQL with pgvector, and answering natural-language questions from the uploaded document set.

## Features

- Upload plain text documents via API
- Split documents into chunks with configurable chunk size and overlap
- Generate embeddings using Ollama models
- Store documents and vectors in PostgreSQL with pgvector
- Retrieve relevant chunks for a question
- Generate answer from the retrieved context using a local LLM
- Run the stack with Docker Compose

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy + asyncpg
- PostgreSQL + pgvector
- Ollama
- Docker / Docker Compose

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   └── documents.py
│   └── services/
│       ├── chunker.py
│       ├── embedder.py
│       ├── generator.py
│       ├── ollama_client.py
│       └── retriever.py
├── migrations/
│   └── 001_init.sql
├── tests/
│   └── test_pipeline.py
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Architecture

The application uses a simple RAG (Retrieval-Augmented Generation) flow:

1. A document is uploaded through the API.
2. The content is split into chunks.
3. Each chunk is embedded with an Ollama embedding model.
4. The embeddings are stored in PostgreSQL with pgvector.
5. When a user asks a question, similar chunks are retrieved by vector similarity.
6. The relevant context is sent to an Ollama chat model to generate the final answer.

## Default Models

The app uses the following Ollama models:

- Embedding model: `nomic-embed-text`
- Generation model: `qwen2.5:1.5b`

These are configured in `app/services/ollama_client.py` and can be adjusted if needed.

## Environment Variables

The main runtime settings are provided by Docker Compose:

- `DATABASE_URL`: PostgreSQL connection string
- `OLLAMA_BASE_URL`: URL of the Ollama service

Example values from the default setup:

```env
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/docqa
OLLAMA_BASE_URL=http://ollama:11434
```

## Local Development

### Prerequisites

- Docker
- Docker Compose
- Python 3.13
- uv (recommended for dependency management)

### Install dependencies

```bash
uv sync
```

### Run the app locally

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

```text
http://localhost:8000
```

## Run with Docker Compose

From the project root:

```bash
docker compose up --build
```

This starts:

- the FastAPI app on port `8000`
- PostgreSQL on port `5432`
- Ollama with a persistent volume for downloaded models

To stop the stack:

```bash
docker compose down
```

## API Endpoints

### Upload a document

```http
POST /documents/
```

Request:
- form-data file field named `file`
- optional query params:
  - `chunk_size` (default: `500`)
  - `overlap` (default: `50`)

Response:
- document metadata including id, filename, and created_at

### List documents

```http
GET /documents/
```

Optional query params:
- `offset`
- `limit`

### Query a document

```http
POST /documents/{document_id}/query
```

Request body:

```json
{
  "question": "What is the main topic of this document?"
}
```

Optional query param:
- `top_k` (default: `5`)

Response:

```json
{
  "answer": "...",
  "sources": ["...", "..."]
}
```

### Delete a document

```http
DELETE /documents/{id}/
```

## Docker Notes

The Docker Compose setup includes a named volume for PostgreSQL:

```yaml
pgdata:/var/lib/postgresql/data
```

And a named volume for Ollama models:

```yaml
ollama_data:/root/.ollama
```

This is intended to persist downloaded models across container restarts. If a model is missing after a restart, check whether the Ollama volume is mounted correctly and whether the container is pointing to the expected model directory.

## Example: Pull Models Manually

If the models are not already present in Ollama, run:

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:1.5b
```

## Troubleshooting

### API cannot connect to PostgreSQL

Check that the database container is healthy and that `DATABASE_URL` matches the service name `db`.

### Ollama model not found

Verify the model has been downloaded and exists in the Ollama container. Then retry the request.

### Document upload fails

The app currently accepts only plain text files (`text/plain`).

## License

This project is currently distributed without a formal license declaration.

## Notes

This project is a small retrieval-based document question answering service intended for local or development use. It is suitable for experimenting with embedding + vector search + LLM-based answer generation using local models.
