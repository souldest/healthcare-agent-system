from backend.app.agents.medical_agent import MedicalAgent
from backend.app.agents.triage_agent import TriageAgent
from backend.app.agents.data_quality_agent import DataQualityAgent
from backend.app.agents.process_agent import ProcessAgent
from backend.app.agents.governance_agent import GovernanceAgent

from backend.app.tools.database_tool import (
    get_case,
    get_documents_for_case
)

from backend.app.audit.service import (
    record_event,
    get_latest_human_review
)


class CaseWorkflow:

    name = "bkk_case_workflow"

    def __init__(self):

        self.medical_agent = MedicalAgent()
        self.triage_agent = TriageAgent()
        self.data_quality_agent = DataQualityAgent()
        self.process_agent = ProcessAgent()
        self.governance_agent = GovernanceAgent()

    def run(
        self,
        db,
        case_id: int
    ):

        # =========================================================
        # 1. Case laden
        # =========================================================

        case = get_case(
            db,
            case_id
        )

        if not case:

            return {
                "workflow": self.name,
                "case_id": case_id,
                "error": "Case not found"
            }

        # =========================================================
        # 2. Dokumente laden
        # =========================================================

        documents = get_documents_for_case(
            db,
            case_id
        )

        # =========================================================
        # 3. Data Quality Agent
        # =========================================================

        data_quality = (
            self.data_quality_agent.run(
                case,
                documents
            )
        )

        record_event(
            case_id=case_id,
            agent="Data Quality Agent",
            action="VALIDATE_CASE",
            status=data_quality.get(
                "quality_status",
                "UNKNOWN"
            ),
            result=str(data_quality),
        )

        # =========================================================
        # 4. Process Agent
        # =========================================================

        process_analysis = (
            self.process_agent.run(
                case,
                data_quality
            )
        )

        record_event(
            case_id=case_id,
            agent="Process Agent",
            action="ANALYZE_WORKFLOW",
            status="ANALYZED",
            result=str(process_analysis),
        )

        # =========================================================
        # 5. Medical Agent
        # =========================================================

        medical_result = (
            self.medical_agent.run(
                db,
                case_id
            )
        )

        record_event(
            case_id=case_id,
            agent="Medical Agent",
            action="MEDICAL_ANALYSIS",
            status="COMPLETED",
            result=str(medical_result),
        )

        # =========================================================
        # 6. Triage Agent
        # =========================================================

        triage_result = (
            self.triage_agent.run(
                case
            )
        )

        record_event(
            case_id=case_id,
            agent="Triage Agent",
            action="RISK_ASSESSMENT",
            status=triage_result.get(
                "priority",
                "UNKNOWN"
            ),
            result=str(triage_result),
        )

        # =========================================================
        # 7. Bereits vorhandene Human Review prüfen
        #
        # Eine APPROVED Review darf bei einem erneuten Workflow-Lauf
        # nicht erneut durch den Governance Agent geöffnet werden.
        # =========================================================

        latest_review = get_latest_human_review(
            case_id
        )

        if (
            latest_review
            and latest_review.get("status") == "APPROVED"
        ):

            governance_result = {
                "agent": "governance_agent",
                "case_id": case_id,
                "decision": "APPROVED",
                "gate": "PASSED",
                "human_review_required": False,
                "human_review_status": "COMPLETED",
                "human_review_decision": "APPROVED",
                "human_review": latest_review,
            }

            record_event(
                case_id=case_id,
                agent="Governance Agent",
                action="HUMAN_REVIEW_GATE",
                status="APPROVED",
                result="Human review approved. Workflow may continue.",
            )

            return self._final_result(
                data_quality=data_quality,
                process_analysis=process_analysis,
                medical_result=medical_result,
                triage_result=triage_result,
                governance_result=governance_result,
                human_review=latest_review,
                status="completed",
                recommendation=(
                    "Fachliche Prüfung abgeschlossen. "
                    "Workflow kann kontrolliert fortgesetzt werden."
                )
            )

        # =========================================================
        # 8. Governance Agent
        # =========================================================

        governance_result = (
            self.governance_agent.run(
                case=case,
                data_quality=data_quality,
                process_analysis=process_analysis,
                medical_result=medical_result,
                triage_result=triage_result
            )
        )

        record_event(
            case_id=case_id,
            agent="Governance Agent",
            action="GOVERNANCE_DECISION",
            status=governance_result.get(
                "decision",
                "UNKNOWN"
            ),
            result=str(governance_result),
        )

        # =========================================================
        # 9. Human Review State
        # =========================================================

        if (
            governance_result.get("decision")
            == "HUMAN_REVIEW"
        ):

            # -----------------------------------------------------
            # REQUEST_CHANGES
            # -----------------------------------------------------

            if (
                latest_review
                and latest_review.get("status")
                == "REQUEST_CHANGES"
            ):

                governance_result = {
                    **governance_result,
                    "decision": "REQUEST_CHANGES",
                    "gate": "CHANGES_REQUIRED",
                    "human_review_required": True,
                    "human_review_status": "CHANGES_REQUIRED",
                    "human_review_decision": "REQUEST_CHANGES",
                    "human_review": latest_review,
                }

                return self._final_result(
                    data_quality=data_quality,
                    process_analysis=process_analysis,
                    medical_result=medical_result,
                    triage_result=triage_result,
                    governance_result=governance_result,
                    human_review=latest_review,
                    status="changes_required",
                    recommendation=(
                        "Änderungen bzw. weitere fachliche Prüfung "
                        "erforderlich. Workflow bleibt pausiert."
                    )
                )

            # -----------------------------------------------------
            # REJECTED
            # -----------------------------------------------------

            if (
                latest_review
                and latest_review.get("status")
                == "REJECTED"
            ):

                governance_result = {
                    **governance_result,
                    "decision": "REJECTED",
                    "gate": "CLOSED",
                    "human_review_required": False,
                    "human_review_status": "COMPLETED",
                    "human_review_decision": "REJECTED",
                    "human_review": latest_review,
                }

                return self._final_result(
                    data_quality=data_quality,
                    process_analysis=process_analysis,
                    medical_result=medical_result,
                    triage_result=triage_result,
                    governance_result=governance_result,
                    human_review=latest_review,
                    status="rejected",
                    recommendation=(
                        "Fall wurde durch die fachliche Prüfung "
                        "abgelehnt. Workflow wurde beendet."
                    )
                )

            # -----------------------------------------------------
            # Noch keine Review
            # -----------------------------------------------------

            record_event(
                case_id=case_id,
                agent="Governance Agent",
                action="HUMAN_REVIEW_GATE",
                status="WAITING_FOR_HUMAN",
                result=(
                    "Workflow paused pending human review."
                ),
            )

            return self._final_result(
                data_quality=data_quality,
                process_analysis=process_analysis,
                medical_result=medical_result,
                triage_result=triage_result,
                governance_result=governance_result,
                human_review=None,
                status="waiting_for_human_review",
                recommendation=(
                    "Human review required. "
                    "Workflow pausiert. "
                    "Fachliche Prüfung durch Mitarbeitende erforderlich."
                )
            )

        # =========================================================
        # 10. Kein Human Review erforderlich
        # =========================================================

        recommendation = (
            self.create_recommendation(
                triage_result,
                data_quality,
                process_analysis,
                governance_result
            )
        )

        return self._final_result(
            data_quality=data_quality,
            process_analysis=process_analysis,
            medical_result=medical_result,
            triage_result=triage_result,
            governance_result=governance_result,
            human_review=latest_review,
            status="completed",
            recommendation=recommendation
        )

    def _final_result(
        self,
        data_quality,
        process_analysis,
        medical_result,
        triage_result,
        governance_result,
        human_review,
        status,
        recommendation
    ):

        return {
            "workflow": self.name,
            "case_id": governance_result.get("case_id"),
            "data_quality": data_quality,
            "process_analysis": process_analysis,
            "medical_analysis": medical_result,
            "triage": triage_result,
            "governance": governance_result,
            "recommendation": recommendation,
            "human_review_required": governance_result.get(
                "human_review_required",
                False
            ),
            "status": status,
            "human_review": human_review,
        }

    def create_recommendation(
        self,
        triage_result,
        data_quality,
        process_analysis,
        governance_result
    ):

        decision = governance_result.get("decision")

        if decision == "APPROVED":
            return (
                "Fachliche Prüfung abgeschlossen. "
                "Workflow kann kontrolliert fortgesetzt werden."
            )

        if decision == "REJECTED":
            return (
                "Fall wurde durch die fachliche Prüfung "
                "abgelehnt."
            )

        if decision == "REQUEST_CHANGES":
            return (
                "Änderungen bzw. weitere fachliche Prüfung "
                "erforderlich."
            )

        if decision == "HUMAN_REVIEW":
            return (
                "Human review required. "
                "Workflow pausiert. Fachliche Prüfung durch Mitarbeitende erforderlich."
            )

        return "Workflow erfolgreich abgeschlossen."
