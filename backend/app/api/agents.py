from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.workflows.case_workflow import CaseWorkflow
from app.audit.service import (
    get_case_history,
    record_human_review,
)


class HumanReviewRequest(BaseModel):
    decision: str
    reviewer: str = "Human Reviewer"
    comment: str | None = None


router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)


@router.get("/analyze/{case_id}")
def analyze_case(
    case_id: int,
    db: Session = Depends(get_db),
):
    try:
        history = get_case_history(case_id)

        # ---------------------------------------------------------
        # Bereits analysierter Case:
        # KEINE erneute Agent-Pipeline starten.
        # Ergebnis wird aus dem Audit-Trail rekonstruiert.
        # ---------------------------------------------------------

        required_actions = {
            "VALIDATE_CASE",
            "ANALYZE_WORKFLOW",
            "MEDICAL_ANALYSIS",
            "RISK_ASSESSMENT",
            "GOVERNANCE_DECISION",
        }

        existing_actions = {
            event.get("action")
            for event in history
        }

        pipeline_completed = required_actions.issubset(
            existing_actions
        )

        if pipeline_completed:

            latest_review = None

            for event in reversed(history):
                if event.get("action") == "HUMAN_REVIEW_DECISION":
                    latest_review = event
                    break

            return _build_result_from_history(
                case_id,
                history,
                latest_review,
            )

        # ---------------------------------------------------------
        # Noch keine vollständige Pipeline:
        # Workflow einmalig ausführen.
        # ---------------------------------------------------------

        workflow = CaseWorkflow()

        result = workflow.run(
            db,
            case_id,
        )

        if result.get("error"):
            raise HTTPException(
                status_code=404,
                detail=result["error"],
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
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


def _build_result_from_history(
    case_id,
    history,
    latest_review,
):
    data_quality = {}
    process_analysis = {}
    medical_analysis = {}
    triage = {}
    governance = {}

    # ---------------------------------------------------------
    # Letzten bekannten Stand jedes Agenten übernehmen.
    # ---------------------------------------------------------

    for event in history:

        action = event.get("action")

        if action == "VALIDATE_CASE":
            data_quality = _parse_result(event)

        elif action == "ANALYZE_WORKFLOW":
            process_analysis = _parse_result(event)

        elif action == "MEDICAL_ANALYSIS":
            medical_analysis = _parse_result(event)

        elif action == "RISK_ASSESSMENT":
            triage = _parse_result(event)

        elif action == "GOVERNANCE_DECISION":
            governance = _parse_result(event)

    # ---------------------------------------------------------
    # Human Review wurde genehmigt.
    # ---------------------------------------------------------

    if latest_review:
        decision = latest_review.get("status")

        if decision == "APPROVED":

            governance = {
                **governance,
                "decision": "APPROVED",
                "gate": "PASSED",
                "human_review_required": False,
                "human_review": latest_review,
            }

            return {
                "workflow": "bkk_case_workflow",
                "case_id": case_id,
                "data_quality": data_quality,
                "process_analysis": process_analysis,
                "medical_analysis": medical_analysis,
                "triage": triage,
                "governance": governance,
                "recommendation": (
                    "Fachliche Prüfung abgeschlossen. "
                    "Workflow kann kontrolliert fortgesetzt werden."
                ),
                "human_review_required": False,
                "status": "completed",
                "human_review": latest_review,
            }

        governance = {
            **governance,
            "human_review": latest_review,
        }

    # ---------------------------------------------------------
    # Human Review weiterhin erforderlich.
    # ---------------------------------------------------------

    if governance.get("decision") == "HUMAN_REVIEW":

        return {
            "workflow": "bkk_case_workflow",
            "case_id": case_id,
            "data_quality": data_quality,
            "process_analysis": process_analysis,
            "medical_analysis": medical_analysis,
            "triage": triage,
            "governance": governance,
            "recommendation": (
                "Workflow pausiert. Eine fachliche Prüfung "
                "durch Mitarbeitende ist erforderlich."
            ),
            "human_review_required": True,
            "status": "waiting_for_human_review",
            "human_review": latest_review,
        }

    # ---------------------------------------------------------
    # Normal abgeschlossen.
    # ---------------------------------------------------------

    return {
        "workflow": "bkk_case_workflow",
        "case_id": case_id,
        "data_quality": data_quality,
        "process_analysis": process_analysis,
        "medical_analysis": medical_analysis,
        "triage": triage,
        "governance": governance,
        "recommendation": (
            "Workflow erfolgreich abgeschlossen."
        ),
        "human_review_required": False,
        "status": "completed",
        "human_review": latest_review,
    }


@router.get("/history/{case_id}")
def case_history(case_id: int):
    return {
        "case_id": case_id,
        "history": get_case_history(case_id),
    }


@router.post("/review/{case_id}")
def submit_human_review(
    case_id: int,
    review: HumanReviewRequest,
):
    try:
        event = record_human_review(
            case_id=case_id,
            decision=review.decision,
            reviewer=review.reviewer,
            comment=review.comment,
        )

        history = get_case_history(case_id)

        latest_review = None

        for history_event in reversed(history):
            if history_event.get("action") == "HUMAN_REVIEW_DECISION":
                latest_review = history_event
                break

        analysis = _build_result_from_history(
            case_id,
            history,
            latest_review,
        )

        return {
            "success": True,
            "case_id": case_id,
            "review": event,
            "analysis": analysis,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
