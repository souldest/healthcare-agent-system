from app.agents.medical_agent import MedicalAgent
from app.agents.triage_agent import TriageAgent
from app.agents.data_quality_agent import DataQualityAgent
from app.agents.process_agent import ProcessAgent
from app.agents.governance_agent import GovernanceAgent

from app.tools.database_tool import (
    get_case,
    get_documents_for_case
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

        # =========================================================
        # 4. Process Agent
        # =========================================================

        process_analysis = (
            self.process_agent.run(
                case,
                data_quality
            )
        )

        # =========================================================
        # 5. Medical Agent
        #
        # Medical Agent verwendet:
        # PostgreSQL + RAG + LLM
        # =========================================================

        medical_result = (
            self.medical_agent.run(
                db,
                case_id
            )
        )

        # =========================================================
        # 6. Triage Agent
        # =========================================================

        triage_result = (
            self.triage_agent.run(
                case
            )
        )

        # =========================================================
        # 7. Governance Agent
        #
        # Entscheidet nicht medizinisch.
        #
        # Er entscheidet ausschließlich:
        # Darf der Workflow kontrolliert weiterlaufen
        # oder ist Human Review erforderlich?
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

        # =========================================================
        # 8. Workflow Recommendation
        # =========================================================

        recommendation = (
            self.create_recommendation(
                triage_result,
                data_quality,
                process_analysis,
                governance_result
            )
        )

        # =========================================================
        # 9. Finales Ergebnis
        # =========================================================

        return {

            "workflow": self.name,

            "case_id": case_id,

            "data_quality": data_quality,

            "process_analysis": process_analysis,

            "medical_analysis": medical_result,

            "triage": triage_result,

            "governance": governance_result,

            "recommendation": recommendation,

            "human_review_required": (
                governance_result[
                    "human_review_required"
                ]
            ),

            "status": "completed"
        }

    def create_recommendation(
        self,
        triage_result,
        data_quality,
        process_analysis,
        governance_result
    ):

        if governance_result.get(
            "decision"
        ) == "HUMAN_REVIEW":

            return (
                "Fachliche Prüfung durch Mitarbeitende vor der "
                "weiteren Bearbeitung erforderlich."
            )

        if data_quality.get(
            "quality_status"
        ) == "REVIEW_REQUIRED":

            return (
                "Manual review required "
                "because case data is incomplete."
            )

        if triage_result.get(
            "priority"
        ) == "HIGH":

            return (
                "Urgent human review recommended."
            )

        return (
            "Controlled workflow continuation. "
            "Next process step: "
            + process_analysis["next_step"]
        )
