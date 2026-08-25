import json

from backend.app.schemas.medical import MedicalAnalysis

from backend.app.agents.base_agent import BaseAgent

from backend.app.llm.provider import LLMProvider
from backend.app.llm.prompts import (
    MEDICAL_ANALYSIS_PROMPT,
    SICK_PAY_ANALYSIS_PROMPT
)

from backend.app.tools.database_tool import (
    get_case,
    get_documents_for_case
)

from backend.app.tools.rag_tool import (
    search_medical_documents
)


class MedicalAgent(BaseAgent):

    name = "medical_agent"


    def __init__(self):

        self.llm = LLMProvider()


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
                "error": "Case not found"
            }


        # =========================================================
        # 2. Dokumente aus PostgreSQL laden
        # =========================================================

        documents = get_documents_for_case(
            db,
            case_id
        )


        # =========================================================
        # 3. RAG-Suche
        #
        # Nur Dokumente des aktuellen Cases verwenden.
        # =========================================================

        rag_results = search_medical_documents(
            query=case.description or "",
            limit=3,
            case_id=case_id
        )


        # =========================================================
        # 4. RAG-Ergebnisse strukturiert extrahieren
        # =========================================================

        findings = []

        rag_documents = rag_results.get(
            "documents",
            []
        )

        rag_metadatas = rag_results.get(
            "metadatas",
            []
        )

        rag_distances = rag_results.get(
            "distances",
            []
        )

        rag_ids = rag_results.get(
            "ids",
            []
        )


        # Chroma liefert verschachtelte Listen:
        #
        # documents = [
        #     ["document 1", "document 2"]
        # ]
        #
        # Deshalb die erste Ergebnisgruppe verwenden.

        document_group = (
            rag_documents[0]
            if rag_documents
            else []
        )

        metadata_group = (
            rag_metadatas[0]
            if rag_metadatas
            else []
        )

        distance_group = (
            rag_distances[0]
            if rag_distances
            else []
        )

        id_group = (
            rag_ids[0]
            if rag_ids
            else []
        )


        for index, content in enumerate(
            document_group
        ):

            metadata = (
                metadata_group[index]
                if index < len(metadata_group)
                else {}
            )

            distance = (
                distance_group[index]
                if index < len(distance_group)
                else None
            )

            document_id = (
                id_group[index]
                if index < len(id_group)
                else None
            )


            findings.append(
                {
                    "id": document_id,

                    "content": content,

                    "distance": distance,

                    "case_id": metadata.get(
                        "case_id"
                    ),

                    "filename": metadata.get(
                        "filename"
                    ),

                    "document_type": metadata.get(
                        "document_type"
                    )
                }
            )


        # =========================================================
        # 5. Texte für LLM vorbereiten
        # =========================================================

        rag_text = "\n".join(
            item["content"]
            for item in findings
            if item.get("content")
        )


        # =========================================================
        # 6. LLM-Prompt erstellen
        # =========================================================

        case_type = (
            case.case_type or ""
        ).upper()

        if case_type in [
            "SICK_PAY",
            "KRANKENGELD",
            "KRANKENGELD-FALLMANAGEMENT"
        ]:
            analysis_prompt = SICK_PAY_ANALYSIS_PROMPT
        else:
            analysis_prompt = MEDICAL_ANALYSIS_PROMPT

        prompt = analysis_prompt.format(
            case_description=case.description or "",
            documents=rag_text
        )


        # =========================================================
        # 7. LLM-Analyse
        # =========================================================

        llm_response = self.llm.generate(
            prompt
        )


        # =========================================================
        # 8. LLM-Antwort validieren
        # =========================================================

        try:

            analysis_json = json.loads(
                llm_response
            )

            analysis = MedicalAnalysis(
                **analysis_json
            ).model_dump()


        except Exception:

            analysis = {

                "summary":
                    "LLM response could not be parsed",

                "findings": [],

                "risk_level":
                    "UNKNOWN",

                "recommended_action":
                    "Manual medical review required"
            }


        # =========================================================
        # 9. Risiko bestimmen
        # =========================================================

        priority = case.priority


        risk = analysis.get(
            "risk_level",
            "LOW"
        )


        if risk not in [
            "LOW",
            "MEDIUM",
            "HIGH"
        ]:

            risk = "LOW"


        # =========================================================
        # 10. Zusätzliche Sicherheitslogik
        #
        # Cardiology + chest pain => mindestens HIGH
        # =========================================================

        description = (
            case.description or ""
        ).lower()


        if (
            case.case_type == "CARDIOLOGY"
            and (
                "chest pain" in description
                or
                "brustschmerz" in description
            )
        ):

            risk = "HIGH"


        # Risiko auch innerhalb der Analyse aktualisieren.

        analysis["risk_level"] = risk


        # =========================================================
        # 10a. Fachliche Schutzlogik für Krankengeldfälle
        #
        # Bei SICK_PAY darf das LLM keine fachfremde medizinische
        # Empfehlung wie z.B. eine kardiologische Untersuchung
        # erzeugen. Der weitere Schritt ist die Prüfung der
        # Arbeitsunfähigkeit und der relevanten Unterlagen.
        # =========================================================

        if case_type in [
            "SICK_PAY",
            "KRANKENGELD",
            "KRANKENGELD-FALLMANAGEMENT"
        ]:

            analysis["recommended_action"] = (
                "Unterlagen zur Arbeitsunfähigkeit und die für "
                "die weitere Anspruchsprüfung erforderlichen "
                "Angaben durch die zuständige Fachstelle prüfen."
            )


        # =========================================================
        # 11. Ergebnis
        # =========================================================

        return {

            "agent":
                self.name,


            "case_id":
                case_id,


            "case_type":
                case.case_type,


            "summary": (
                f"Case {case_id} analyzed. "
                f"{len(documents)} medical documents found."
            ),


            # PostgreSQL-Dokumente
            "documents": [

                {
                    "id": d.id,

                    "filename": d.filename,

                    "document_type":
                        d.document_type,

                    "embedding_id":
                        d.embedding_id
                }

                for d in documents
            ],


            # RAG-Ergebnisse
            "rag_findings":
                findings,


            # Rückwärtskompatibel:
            # Nur die Texte der RAG-Ergebnisse.
            "findings": [

                item["content"]

                for item in findings

                if item.get("content")
            ],


            # LLM-Analyse
            "analysis":
                analysis,


            # Finales Risiko
            "risk_level":
                risk,


            # Case-Priorität
            "priority":
                priority
        }
