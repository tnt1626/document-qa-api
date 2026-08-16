import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.routers.documents import doc_router
from app.services.ollama_client import client, EMBED_MODEL_NAME, GENERATE_MODEL_NAME

logger = logging.getLogger(__name__)

async def pull_ollama_models():
    try:
        logger.info(f"Starting to pull Ollama models: {EMBED_MODEL_NAME}, {GENERATE_MODEL_NAME}")
        await client.pull(EMBED_MODEL_NAME)
        await client.pull(GENERATE_MODEL_NAME)
        logger.info("Successfully pulled Ollama models.")
    except Exception as e:
        logger.error(f"Failed to pull Ollama models: {e}. Application will continue starting, but Ollama might be unavailable.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(pull_ollama_models())
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

