from app.agents.base_agent import BaseAgent


class GovernanceAgent(BaseAgent):

    name = "governance_agent"

    def run(
        self,
        case,
        data_quality,
        process_analysis,
        medical_result,
        triage_result
    ):

        rules_triggered = []

        priority = (
            triage_result.get("priority")
            or "LOW"
        )

        quality_status = (
            data_quality.get("quality_status")
            or "UNKNOWN"
        )

        risk_level = (
            medical_result.get("risk_level")
            or "UNKNOWN"
        )

        # ---------------------------------------------------------
        # Rule 1: Datenqualität
        # ---------------------------------------------------------

        if quality_status == "REVIEW_REQUIRED":

            rules_triggered.append(
                "DATA_QUALITY_REVIEW"
            )

        # ---------------------------------------------------------
        # Rule 2: Hohes Triage-Risiko
        # ---------------------------------------------------------

        if priority == "HIGH":

            rules_triggered.append(
                "HIGH_RISK"
            )

        # ---------------------------------------------------------
        # Rule 3: Medizinisches Risiko
        # ---------------------------------------------------------

        if risk_level == "HIGH":

            rules_triggered.append(
                "MEDICAL_REVIEW_REQUIRED"
            )

        # ---------------------------------------------------------
        # Governance Decision
        # ---------------------------------------------------------

        human_review_required = (
            len(rules_triggered) > 0
        )

        if human_review_required:

            decision = "HUMAN_REVIEW"
            gate = "ACTIVE"

            if "HIGH_RISK" in rules_triggered:

                reason = (
                    "Hochrisikofall erkannt. "
                    "Eine qualifizierte fachliche Prüfung durch "
                    "Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
                )

            elif "DATA_QUALITY_REVIEW" in rules_triggered:

                reason = (
                    "Case data is incomplete or inconsistent. "
                    "Manual review is required."
                )

            else:

                reason = (
                    "Medical review is required "
                    "before further processing."
                )

        else:

            decision = "CONTROLLED_CONTINUE"
            gate = "PASS"

            reason = (
                "No governance rule requiring human review "
                "was triggered."
            )

        return {

            "agent": self.name,

            "case_id": case.id,

            "decision": decision,

            "gate": gate,

            "human_review_required": (
                human_review_required
            ),

            "reason": reason,

            "rules_triggered": rules_triggered,

            "risk_level": risk_level,

            "triage_priority": priority,

            "data_quality_status": quality_status
        }
