from ollama import AsyncClient

MODEL_NAME = "nomic-embed-text"

client = AsyncClient()

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
        response = await client.embed(model=MODEL_NAME, input=text)
        return response.embeddings[0]
    except Exception as e:
        print(f"Error in embedding with {MODEL_NAME}: {e}")
        raise e

