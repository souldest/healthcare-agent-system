from fastapi import APIRouter, Depends, HTTPException, Query
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
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
):
    try:
        history = get_case_history(case_id)

        # =========================================================
        # Bereits vorhandene Human Review prüfen.
        #
        # Nach einer Human Review darf /analyze/{case_id}
        # NICHT erneut die Agent-Pipeline starten.
        # =========================================================

        latest_review = None

        for event in reversed(history):
            if event.get("action") == "HUMAN_REVIEW_DECISION":
                latest_review = event
                break

        if latest_review is not None and not refresh:
            return _build_result_from_history(
                case_id,
                history,
                latest_review,
            )

        # =========================================================
        # Prüfen, ob die normale Pipeline bereits vollständig ist.
        # =========================================================

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

        if pipeline_completed and not refresh:
            return _build_result_from_history(
                case_id,
                history,
                None,
            )

        # =========================================================
        # Nur wirklich neue Cases starten die Workflow-Pipeline.
        # =========================================================

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

    # =========================================================
    # Letzten bekannten Agentenstand übernehmen
    # =========================================================

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

    # =========================================================
    # Human Review
    # =========================================================

    if latest_review:

        decision = (
            str(
                latest_review.get("status", "")
            )
            .upper()
            .strip()
        )

        # -----------------------------------------------------
        # APPROVED
        # -----------------------------------------------------

        if decision == "APPROVED":

            governance = {
                **governance,

                "decision": "APPROVED",

                "gate": "PASSED",

                "human_review_required": False,

                "human_review_status": "COMPLETED",

                "human_review_decision": "APPROVED",

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

        # -----------------------------------------------------
        # REQUEST_CHANGES
        # -----------------------------------------------------

        if decision == "REQUEST_CHANGES":

            governance = {
                **governance,

                "decision": "REQUEST_CHANGES",

                "gate": "CHANGES_REQUIRED",

                "human_review_required": True,

                "human_review_status": "CHANGES_REQUIRED",

                "human_review_decision": "REQUEST_CHANGES",

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
                    "Änderungen bzw. weitere fachliche Prüfung "
                    "erforderlich. Workflow bleibt pausiert."
                ),

                "human_review_required": True,

                "status": "changes_required",

                "human_review": latest_review,
            }

        # -----------------------------------------------------
        # REJECTED
        # -----------------------------------------------------

        if decision == "REJECTED":

            governance = {
                **governance,

                "decision": "REJECTED",

                "gate": "CLOSED",

                "human_review_required": False,

                "human_review_status": "COMPLETED",

                "human_review_decision": "REJECTED",

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
                    "Fall wurde durch die fachliche Prüfung "
                    "abgelehnt. Workflow wurde beendet."
                ),

                "human_review_required": False,

                "status": "rejected",

                "human_review": latest_review,
            }

        # -----------------------------------------------------
        # Unbekannte Entscheidung
        # -----------------------------------------------------

        governance = {
            **governance,
            "human_review": latest_review,
        }

    # =========================================================
    # Human Review erforderlich
    # =========================================================

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

    # =========================================================
    # Normal abgeschlossen
    # =========================================================

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
def case_history(
    case_id: int,
):
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

        # =====================================================
        # Human Review speichern
        # =====================================================

        event = record_human_review(
            case_id=case_id,
            decision=review.decision,
            reviewer=review.reviewer,
            comment=review.comment,
        )

        # =====================================================
        # Aktuellen Audit Trail laden
        # =====================================================

        history = get_case_history(
            case_id
        )

        latest_review = None

        for history_event in reversed(history):

            if (
                history_event.get("action")
                == "HUMAN_REVIEW_DECISION"
            ):

                latest_review = history_event

                break

        # =====================================================
        # Ergebnis für Frontend aufbauen
        # =====================================================

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
