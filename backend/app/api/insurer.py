from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.base import get_db
from backend.app.models.case import Case
from backend.app.audit.service import get_case_history


router = APIRouter(
    prefix="/insurer",
    tags=["Insurer Portal"],
)


def _parse_result(event):
    result = event.get("result")

    if not isinstance(result, str):
        return result or {}

    try:
        import ast

        parsed = ast.literal_eval(result)

        if isinstance(parsed, dict):
            return parsed

    except (ValueError, SyntaxError):
        pass

    return {}


def _latest_agent_result(history, action):
    result = {}

    for event in history:
        if event.get("action") == action:
            result = _parse_result(event)

    return result


@router.get("/cases")
def list_insurer_cases(
    db: Session = Depends(get_db),
):
    cases = (
        db.query(Case)
        .order_by(Case.id)
        .all()
    )

    result = []

    for case in cases:
        history = get_case_history(case.id)

        latest_review = None

        for event in reversed(history):
            if event.get("action") == "HUMAN_REVIEW_DECISION":
                latest_review = event
                break

        governance = _latest_agent_result(
            history,
            "GOVERNANCE_DECISION",
        )

        triage = _latest_agent_result(
            history,
            "RISK_ASSESSMENT",
        )

        medical = _latest_agent_result(
            history,
            "MEDICAL_ANALYSIS",
        )

        review_approved = (
            latest_review is not None
            and latest_review.get("status") == "APPROVED"
        )

        result.append({
            "case_id": case.id,
            "case_type": case.case_type,
            "status": (
                "APPROVED"
                if review_approved
                else case.status
            ),
            "priority": (
                triage.get("priority")
                or case.priority
                or "NORMAL"
            ),
            "description": case.description,
            "workflow_status": (
                "COMPLETED"
                if review_approved
                else "IN_REVIEW"
            ),
            "review_status": (
                "APPROVED"
                if review_approved
                else "PENDING"
            ),
            "recommended_action": (
                medical.get("analysis", {})
                .get("recommended_action")
            ),
        })

    return {
        "cases": result,
        "count": len(result),
    }


@router.get("/cases/{case_id}")
def get_insurer_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    case = (
        db.query(Case)
        .filter(Case.id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found",
        )

    history = get_case_history(case_id)

    medical = _latest_agent_result(
        history,
        "MEDICAL_ANALYSIS",
    )

    triage = _latest_agent_result(
        history,
        "RISK_ASSESSMENT",
    )

    process = _latest_agent_result(
        history,
        "ANALYZE_WORKFLOW",
    )

    latest_review = None

    for event in reversed(history):
        if event.get("action") == "HUMAN_REVIEW_DECISION":
            latest_review = event
            break

    review_approved = (
        latest_review is not None
        and latest_review.get("status") == "APPROVED"
    )

    patient = case.patient

    documents = medical.get("documents", [])

    return {
        "case_id": case.id,

        "patient": {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "insurance_number": patient.insurance_number,
        },

        "case": {
            "case_type": case.case_type,
            "description": case.description,
            "priority": (
                triage.get("priority")
                or case.priority
                or "NORMAL"
            ),
        },

        "workflow": {
            "status": (
                "COMPLETED"
                if review_approved
                else "IN_REVIEW"
            ),
            "current_step": process.get("current_step"),
            "next_step": process.get("next_step"),
        },

        "decision": {
            "review_status": (
                "APPROVED"
                if review_approved
                else "PENDING"
            ),
            "gate": (
                "PASSED"
                if review_approved
                else "ACTIVE"
            ),
            "recommended_action": (
                medical.get("analysis", {})
                .get("recommended_action")
            ),
        },

        "documents": [
            {
                "filename": document.get("filename"),
                "document_type": document.get(
                    "document_type"
                ),
            }
            for document in documents
        ],
    }
