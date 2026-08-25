from sqlalchemy.orm import Session

from backend.app.models.patient import Patient
from backend.app.schemas.patient import PatientCreate


def create_patient(
        db: Session,
        patient: PatientCreate
):

    db_patient = Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        insurance_number=patient.insurance_number
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    return db_patient



def get_patients(db: Session):

    return db.query(Patient).all()
