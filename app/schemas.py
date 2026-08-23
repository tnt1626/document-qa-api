import uuid
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    created_at: datetime

class DocumentUploadResponse(DocumentListItem):
    pass

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class AgentQuery(QueryRequest):
    document_id: uuid.UUID | None = None
    chat_history: list[ChatMessage] | None = None

class AgentResponse(BaseModel):
    answer: str 