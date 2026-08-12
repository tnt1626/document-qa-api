from app.services.ollama_client import EMBED_MODEL_NAME, client

async def embed_text(text: str) -> list[float]:
    """Embedd user query using nomic-embed-text via Ollama

    Args:
        text (str): user query input

    Raises:
        e: detail error

    Returns:
        list[float]: text input represented in vector
    """
    try:
        response = await client.embed(model=EMBED_MODEL_NAME, input=text)
        return response.embeddings[0]
    except Exception as e:
        print(f"Error in embedding with {EMBED_MODEL_NAME}: {e}")
        raise e

