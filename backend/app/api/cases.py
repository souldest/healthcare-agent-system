from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseResponse


router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)


@router.post("/", response_model=CaseResponse)
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db)
):
    db_case = Case(
        patient_id=case.patient_id,
        case_type=case.case_type,
        status=case.status,
        priority=case.priority,
        description=case.description
    )

    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    return db_case


@router.get("/", response_model=list[CaseResponse])
def list_cases(
    db: Session = Depends(get_db)
):
    return db.query(Case).all()
