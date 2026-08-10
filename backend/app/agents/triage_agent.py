from app.agents.base_agent import BaseAgent


class TriageAgent(BaseAgent):

    name = "triage_agent"


    def run(
        self,
        case
    ):

        description = (
            case.description or ""
        ).lower()


        priority = "LOW"
        reason = "No urgent symptoms detected"


        # Herz-Kreislauf Notfälle
        if (
            "chest pain" in description
            or "chest pressure" in description
            or "shortness of breath" in description
        ):
            priority = "HIGH"
            reason = (
                "Mögliche Hinweise auf einen akuten kardiologischen Notfall erkannt"
            )


        # Mittlere Dringlichkeit
        elif (
            "pain" in description
            or "fever" in description
            or "infection" in description
        ):
            priority = "MEDIUM"
            reason = (
                "Symptoms require medical evaluation"
            )


        return {
            "agent": self.name,
            "case_id": case.id,
            "priority": priority,
            "reason": reason
        }
