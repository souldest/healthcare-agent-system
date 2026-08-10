from pydantic import BaseModel


class PatientCreate(BaseModel):

    first_name: str
    last_name: str
    insurance_number: str


class PatientResponse(BaseModel):

    id: int
    first_name: str
    last_name: str
    insurance_number: str

    class Config:
        from_attributes = True
