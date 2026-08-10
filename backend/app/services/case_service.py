from sqlalchemy.orm import Session
from app.models.case import Case
from app.schemas.case import CaseCreate

def create_case(db: Session, case_data: CaseCreate):

    case = Case(
        patient_id=case_data.patient_id,
        case_type=case_data.case_type,
        status=case_data.status,
        priority=case_data.priority,
        description=case_data.description
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def get_cases(db: Session):

    return db.query(Case).all()
