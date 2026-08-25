from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.patient import PatientCreate, PatientResponse
from backend.app.repositories.patient_repository import (
    create_patient,
    get_patients
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse
)
def add_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):

    return create_patient(
        db,
        patient
    )


@router.get(
    "/",
    response_model=list[PatientResponse]
)
def list_patients(
    db: Session = Depends(get_db)
):

    return get_patients(db)
