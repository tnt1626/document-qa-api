import uuid
from datetime import datetime
from pydantic import BaseModel

class DocumentListItem(BaseModel):
    document_id: uuid.UUID
    filename: str
    created_at: datetime

class DocumentUploadResponse(DocumentListItem):
    chunk_count: int

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]