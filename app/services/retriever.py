from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embedder import embed_text
from app.models import Chunk

async def retrieve_vec(question: str, top_k: int, db: AsyncSession):
    embed_vec = await embed_text(question)
    chunks = (
        await db.scalars(
            select(Chunk)
            .order_by(
                Chunk.embedding.cosine_distance(embed_vec)
            )
            .limit(top_k)
        )
    ).all()
    return chunks
