from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import DocumentUploadResponse
from app.database import get_db
from app.models import Document

doc_router = APIRouter(prefix="documents")

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
