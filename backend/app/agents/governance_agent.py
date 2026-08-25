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

        # =========================================================
        # Rule 1: Datenqualität
        # =========================================================

        if quality_status == "REVIEW_REQUIRED":
            rules_triggered.append(
                "DATA_QUALITY_REVIEW"
            )

        # =========================================================
        # Rule 2: Medizinisches Risiko
        # =========================================================

        if risk_level == "HIGH":
            rules_triggered.append(
                "MEDICAL_REVIEW_REQUIRED"
            )

        # =========================================================
        # Rule 3: Hohe Triage-Priorität
        # =========================================================

        if priority == "HIGH":
            rules_triggered.append(
                "HIGH_RISK"
            )

        # =========================================================
        # Governance Decision
        # =========================================================

        human_review_required = (
            len(rules_triggered) > 0
        )

        if human_review_required:

            decision = "HUMAN_REVIEW"
            gate = "ACTIVE"

            if "DATA_QUALITY_REVIEW" in rules_triggered:

                reason = (
                    "Die Falldaten sind unvollständig oder "
                    "inkonsistent. Eine manuelle Prüfung ist erforderlich."
                )

            elif (
                "MEDICAL_REVIEW_REQUIRED"
                in rules_triggered
            ):

                reason = (
                    "Ein erhöhtes medizinisches Risiko wurde erkannt. "
                    "Eine qualifizierte fachliche Prüfung durch "
                    "Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
                )

            else:

                reason = (
                    "Eine hohe Triage-Priorität wurde erkannt. "
                    "Eine qualifizierte fachliche Prüfung durch "
                    "Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
                )

        else:

            decision = "CONTROLLED_CONTINUE"
            gate = "PASS"

            reason = (
                "Keine Governance-Regel erfordert eine "
                "fachliche Prüfung."
            )

        return {
            "agent": self.name,
            "case_id": case.id,
            "decision": decision,
            "gate": gate,
            "human_review_required": human_review_required,
            "reason": reason,
            "rules_triggered": rules_triggered,
            "risk_level": risk_level,
            "triage_priority": priority,
            "data_quality_status": quality_status,
        }
