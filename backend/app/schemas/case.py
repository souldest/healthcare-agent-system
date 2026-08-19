from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    patient_id: int
    case_type: str
    status: str = "OPEN"
    priority: str = "NORMAL"
    description: str | None = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    case_type: str
    status: str
    priority: str
    description: str | None
