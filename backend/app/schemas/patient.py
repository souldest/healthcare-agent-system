from pydantic import BaseModel, ConfigDict


class PatientCreate(BaseModel):

    first_name: str
    last_name: str
    insurance_number: str


class PatientResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    insurance_number: str
