import uuid
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models import FileStatus

class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: FileStatus
    filename: str
    updated_at: datetime
    created_at: datetime

class DocumentUploadResponse(DocumentListItem):
    pass

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    token: int
    sources: list[str]

class ToolCallDetail(BaseModel):
    id: str
    name: str
    arguments: dict
    result: str | None = None

class ThoughtStep(BaseModel):
    loop_index: int
    token: int
    thought: str | None = None
    tool_calls: list[ToolCallDetail] = []

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class AgentQuery(QueryRequest):
    document_id: uuid.UUID | None = None
    chat_history: list[ChatMessage] | None = None

class AgentResponse(BaseModel):
    answer: str 
    thought_steps: list[ThoughtStep] = []