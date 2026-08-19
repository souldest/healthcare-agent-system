from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    case_id: int
    filename: str
    document_type: str | None = None
    content: str | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    filename: str
    document_type: str | None
    content: str | None
    embedding_id: str | None
