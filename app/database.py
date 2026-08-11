from typing import AsyncGenerator, Any
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DB_URL = "postgresql+asyncpg://user:password@0.0.0.0:5432/docqa"

engine = create_async_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        yield session
