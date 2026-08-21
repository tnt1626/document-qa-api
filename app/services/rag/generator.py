import uuid
import ollama
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.services.rag.retriever import retrieve_vec
from app.services.ollama_client import GENERATE_MODEL_NAME, client

class OllamaConnectionError(Exception): 
    pass

class OllamaModelNotFound(Exception): 
    pass

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(min=1, max=10),
    retry=retry_if_exception_type(ollama.RequestError)
)
async def generate(
    question: str, 
    document_id: uuid.UUID, 
    top_k: int, 
    db: AsyncSession
):
    chunks = await retrieve_vec(question, document_id, top_k, db)
    if not chunks:
        return {
            "answer": "",
            "sources": []
        }

    context = ""
    for chunk in chunks:
        context += f"{chunk.content}\n"

    system_prompt = f"""You are a helpful assistant. Answer the question based ONLY on the context below.
Do not use any knowledge outside of the provided context.
If the answer cannot be found in the context, respond exactly with: "I don't know based on the provided document."

Context:
{context}
"""
    try:
        response = await client.chat(
            model=GENERATE_MODEL_NAME,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": question
                }
            ]
        )

        return {
            "answer": response.message.content,
            "sources": [chunk.content for chunk in chunks]
        }
    except ollama.RequestError:
        raise OllamaConnectionError()
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise OllamaModelNotFound()
        raise
    except Exception as e:
        raise RuntimeError(f"Generate failed: {e}")
