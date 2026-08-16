import os
from ollama import AsyncClient

EMBED_MODEL_NAME = "nomic-embed-text"
GENERATE_MODEL_NAME = "qwen2.5:1.5b"

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

client = AsyncClient(host=OLLAMA_URL)