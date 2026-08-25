from backend.app.agents.base_agent import BaseAgent


class ProcessAgent(BaseAgent):

    name = "process_agent"

    def run(self, case, data_quality):

        case_type = (
            case.case_type or ""
        ).upper()

        # =========================================================
        # BKK-nahe Prozesszuordnung
        # =========================================================

        if case_type in [
            "SICK_PAY",
            "KRANKENGELD",
            "KRANKENGELD-FALLMANAGEMENT"
        ]:

            process = "Krankengeld-Fallmanagement"
            current_step = "Fallprüfung"
            next_step = "Unterlagen und Anspruch prüfen"

        elif case_type in [
            "CARE",
            "PFLEGE",
            "PFLEGE_SCHUTZ"
        ]:

            process = "Pflegeberatung"
            current_step = "Fallaufnahme"
            next_step = "Pflegebedarf prüfen"

        elif case_type in [
            "CARDIOLOGY",
            "MEDICAL",
            "GENERAL"
        ]:

            process = "Gesundheitsbezogener Leistungsfall"
            current_step = "Medizinische Fallanalyse"
            next_step = "Fachliche Prüfung"

        else:

            process = "Allgemeiner Leistungsfall"
            current_step = "Fallaufnahme"
            next_step = "Sachbearbeiterprüfung"

        # =========================================================
        # Data Quality Gate
        #
        # Unvollständige oder problematische Daten dürfen nicht
        # automatisch weiterverarbeitet werden.
        # =========================================================

        quality_status = (
            data_quality.get("quality_status")
        )

        quality_issues = (
            data_quality.get("issues", [])
        )

        if quality_status != "VALID":

            next_step = (
                "Daten vervollständigen "
                "und manuell prüfen"
            )

            human_review_required = True

        else:

            human_review_required = False

        # =========================================================
        # Ergebnis
        # =========================================================

        return {

            "agent": self.name,

            "case_id": case.id,

            "process": process,

            "current_step": current_step,

            "next_step": next_step,

            "data_quality_status": quality_status,

            "data_quality_issues": quality_issues,

            "human_review_required":
                human_review_required

        }

