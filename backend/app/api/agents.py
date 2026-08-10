from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.workflows.case_workflow import CaseWorkflow


router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


@router.get("/analyze/{case_id}")
def analyze_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    try:
        workflow = CaseWorkflow()

        result = workflow.run(
            db,
            case_id
        )

        if result.get("error"):
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

