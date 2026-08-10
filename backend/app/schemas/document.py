from datetime import datetime
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    case_id: int
    filename: str
    document_type: str | None = None
    content: str | None = None


class DocumentResponse(BaseModel):
    id: int
    case_id: int
    filename: str
    document_type: str | None
    content: str | None
    embedding_id: str | None

    class Config:
        from_attributes = True
