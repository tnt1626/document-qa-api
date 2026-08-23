import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag.embedder import embed_text
from app.models import Chunk

async def retrieve_vec(question: str, document_id: uuid.UUID | None, top_k: int, db: AsyncSession):
    """
    Retrieve document by user question
    Args:
        question (str): user query
        document_id (uuid.UUID): the id of user's document
        top_k (int): number of chunks used as document for response
        db (AsyncSession): database session

    """
    embed_vec = await embed_text(question)
    selected_obj = select(Chunk)
    if document_id:
        selected_obj = selected_obj.where(Chunk.document_id == document_id)

    chunks = (
        await db.scalars(
            selected_obj
            .order_by(
                Chunk.embedding.cosine_distance(embed_vec)
            )
            .limit(top_k)
        )
    ).all()
    return chunks
