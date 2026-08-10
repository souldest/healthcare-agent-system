from pydantic import BaseModel


class CaseCreate(BaseModel):
    patient_id: int
    case_type: str
    status: str = "OPEN"
    priority: str = "NORMAL"
    description: str | None = None


class CaseResponse(BaseModel):
    id: int
    patient_id: int
    case_type: str
    status: str
    priority: str
    description: str | None

    class Config:
        from_attributes = True
