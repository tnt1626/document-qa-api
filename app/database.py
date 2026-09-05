import os
import uuid
from sqlalchemy import select
from dotenv import load_dotenv
from typing import AsyncGenerator, Any
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models import FileStatus, Document

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/docqa")
if DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        yield session

async def update_doc_status(doc_id: uuid.UUID, status: FileStatus):
    async with SessionLocal() as session:
        doc = await session.scalar(select(Document).where(Document.id == doc_id))
        if doc:
            doc.status = status
            await session.commit()