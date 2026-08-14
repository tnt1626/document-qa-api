from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.routers.documents import doc_router
from app.services.ollama_client import client, EMBED_MODEL_NAME, GENERATE_MODEL_NAME

async def pull_ollama_models():
    await client.pull(EMBED_MODEL_NAME)
    await client.pull(GENERATE_MODEL_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pull_ollama_models()
    yield

app = FastAPI(
    title="Document Q&A API",
    description="Upload documents and query them using natural language.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(doc_router)

@app.exception_handler(Exception)
async def global_exception_hanlder(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

