from sqlalchemy.orm import Session

from backend.app.models.patient import Patient
from backend.app.models.case import Case
from backend.app.models.document import Document


def get_patient(
    db: Session,
    patient_id: int
):
    return (
        db.query(Patient)
        .filter(
            Patient.id == patient_id
        )
        .first()
    )


def get_case(
    db: Session,
    case_id: int
):
    return (
        db.query(Case)
        .filter(
            Case.id == case_id
        )
        .first()
    )


def get_documents_for_case(
    db: Session,
    case_id: int
):
    return (
        db.query(Document)
        .filter(
            Document.case_id == case_id
        )
        .all()
    )
