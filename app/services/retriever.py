# import numpy as np
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database import get_db
# from app.services.embedder import embed_text

# async def retrieve_vec(question: str, top_k: int, db: AsyncSession = Depends(get_db)):
#     embed_vec = np.array(await embed_text(question))
