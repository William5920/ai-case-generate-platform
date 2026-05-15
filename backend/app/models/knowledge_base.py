from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: UUID
    user_id: UUID
    file_path: str
    file_size: int
    file_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentSlice(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    chunk_id: int
    
    class Config:
        from_attributes = True

class KnowledgeRecallParams(BaseModel):
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class RecallTestRequest(BaseModel):
    query: str
    params: KnowledgeRecallParams = KnowledgeRecallParams()

class RecallTestResponse(BaseModel):
    query: str
    results: list[dict]
    total: int
