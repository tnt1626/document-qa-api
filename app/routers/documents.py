import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.database import get_db
from app.models import Document
from app.services.generator import generate, OllamaConnectionError, OllamaModelNotFound
from app.schemas import DocumentUploadResponse, DocumentListItem, QueryRequest, QueryResponse

doc_router = APIRouter(prefix="/documents")

@doc_router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=400,
            detail="Only text is supported"
        )
    
    try:
        content = await file.read()
        text = content.decode("utf-8")

        doc = Document(
            filename=file.filename,
            content=text
        )

        try:
            db.add(doc)
            await db.commit()
            await db.refresh(doc)
        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to save document"
            )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        created_at=doc.created_at,
        chunk_count=0  
    )


@doc_router.post("/{document_id}/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    document_id: uuid.UUID,
    top_k: int = 5,
    db: AsyncSession = Depends(get_db),
):
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

        return QueryResponse(**response)
    except OllamaConnectionError:
        raise HTTPException(status_code=503, detail="AI service unavailable")
    except OllamaModelNotFound:
        raise HTTPException(status_code=500, detail="Model not configured")


    
    

@doc_router.get("/", response_model=list[DocumentListItem])
async def list_documents(
    offset: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
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

    return {
        "deleted": True
    }