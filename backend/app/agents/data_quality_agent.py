from backend.app.agents.base_agent import BaseAgent


class DataQualityAgent(BaseAgent):

    name = "data_quality_agent"

    def run(self, case, documents):

        issues = []

        if not case.description:
            issues.append(
                "Case description is missing"
            )

        if not case.case_type:
            issues.append(
                "Case type is missing"
            )

        if not documents:
            issues.append(
                "Keine unterstützenden Dokumente gefunden"
            )

        quality_status = (
            "VALID"
            if not issues
            else "REVIEW_REQUIRED"
        )

        return {
            "agent": self.name,
            "case_id": case.id,
            "quality_status": quality_status,
            "issues": issues,
            "document_count": len(documents),
        }
