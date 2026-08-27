import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, BackgroundTasks
from app.models import Document, Chunk
from app.database import get_db, SessionLocal
from app.services.rag.chunker import chunk_text
from app.services.rag.embedder import embed_text
from app.services.rag.generator import generate, OllamaConnectionError, OllamaModelNotFound
from app.schemas import DocumentUploadResponse, DocumentListItem, QueryRequest, QueryResponse

CONTENT_TYPES = [
    "text/html",
    "text/css",
    "text/csv",
    "text/xml",
    "text/plain",
    "text/markdown",
    "application/json"
]

logger = logging.getLogger(__name__)

doc_router = APIRouter(prefix="/documents")

async def upload(doc_id: uuid.UUID, content: str, chunk_size: int, overlap: int):
    try:
        chunks = chunk_text(content, chunk_size, overlap)
    except Exception as e:
        logger.error(f"Failed to chunk document {doc_id}: {e}")
        return

    async with SessionLocal() as session:
        try:
            for idx, chunk in enumerate(chunks):
                vec = await embed_text(chunk)
                session.add(Chunk(
                    document_id=doc_id,
                    content=chunk,
                    embedding=vec,
                    chunk_index=idx
                ))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save chunks for document {doc_id}: {e}")


@doc_router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    chunk_size: int = 500,
    overlap: int = 50,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a text document and process it for Q&A."""
    if file.content_type not in CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Format as {file.content_type} is not supported"
        )
    
    try:
        content = await file.read()
        text = content.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read file")

    try:
        doc = Document(filename=file.filename, content=text)
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        logger.info(f"Saved metadata for document '{file.filename}' (ID: {doc.id}). Starting background chunking & embedding.")
    except Exception:
        await db.rollback()
        logger.exception(f"Failed to save metadata for document '{file.filename}'")
        raise HTTPException(status_code=500, detail="Failed to save document")

    background_tasks.add_task(
        upload,
        doc_id=doc.id,
        content=text,
        chunk_size=chunk_size,
        overlap=overlap
    )
    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        created_at=doc.created_at,
    )


@doc_router.post("/{document_id}/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    document_id: uuid.UUID,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """Query a document using natural language and get an AI-generated answer."""
    logger.info(f"Querying document {document_id} with question: '{request.question}'")
    doc = await db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    try:
        response = await generate(
            question=request.question,
            document_id=document_id,
            top_k=top_k,
            db=db
        )
        logger.info(f"Successfully generated answer for document {document_id}")

        return QueryResponse(**response)
    except OllamaConnectionError as e:
        logger.error(f"Ollama connection error for document {document_id}: {e}")
        raise HTTPException(status_code=503, detail="AI service unavailable")
    except OllamaModelNotFound:
        raise HTTPException(status_code=500, detail="Model not configured")
    

@doc_router.get("/", response_model=list[DocumentListItem])
async def list_documents(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Query all documents"""
    items = (
        await db.scalars(
            select(Document)
            .offset(offset)
            .limit(limit)
        )
    ).all()

    items = [DocumentListItem.model_validate(item) for item in items]
    return items

@doc_router.delete("/{id}/", response_model=dict)
async def delete_document(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete document with id if existed"""
    item = (
        await db.scalar(
            select(Document)
            .where(Document.id == id)
        )
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Not found document"
        )

    await db.delete(item)
    await db.commit()

    logger.info(f"Document with ID {id} has been permanently deleted from database.")
    return {
        "deleted": True
    }