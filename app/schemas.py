import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    filename: str
    created_at: datetime

class DocumentUploadResponse(DocumentListItem):
    pass

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]