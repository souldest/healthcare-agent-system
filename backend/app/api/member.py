from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.base import get_db
from backend.app.models.patient import Patient
from backend.app.models.case import Case
from backend.app.rag.embeddings import create_embedding
from backend.app.rag.vector_store import search_documents


router = APIRouter(
    prefix="/member",
    tags=["Member Portal"],
)


class MemberChatRequest(BaseModel):
    question: str


def get_patient(
    insurance_number: str,
    db: Session,
):
    patient = (
        db.query(Patient)
        .filter(
            Patient.insurance_number == insurance_number
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Versicherter nicht gefunden.",
        )

    return patient


@router.get("/{insurance_number}")
def get_member(
    insurance_number: str,
    db: Session = Depends(get_db),
):
    patient = get_patient(
        insurance_number,
        db,
    )

    return {
        "patient": {
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "insurance_number": patient.insurance_number,
        }
    }


@router.get("/{insurance_number}/cases")
def get_member_cases(
    insurance_number: str,
    db: Session = Depends(get_db),
):
    patient = get_patient(
        insurance_number,
        db,
    )

    cases = (
        db.query(Case)
        .filter(Case.patient_id == patient.id)
        .order_by(Case.id.desc())
        .all()
    )

    result = []

    for case in cases:
        if case.status == "OPEN":
            status = "IN BEARBEITUNG"
        else:
            status = case.status

        result.append({
            "case_id": case.id,
            "status": status,
        })

    return {
        "cases": result,
        "count": len(result),
    }


@router.post("/{insurance_number}/chat")
def member_chat(
    insurance_number: str,
    request: MemberChatRequest,
    db: Session = Depends(get_db),
):
    patient = get_patient(
        insurance_number,
        db,
    )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Bitte geben Sie eine Frage ein.",
        )

    sensitive_keywords = [
        "diagnose",
        "medizinisch",
        "behandlung",
        "therapie",
        "übernimmt",
        "übernahme",
        "kostenübernahme",
        "erstattet",
        "erstatten",
        "genehmigt",
        "genehmigung",
    ]

    requires_human = any(
        keyword in question.lower()
        for keyword in sensitive_keywords
    )

    if requires_human:
        return {
            "answer": (
                "Diese Frage betrifft eine individuelle "
                "medizinische oder leistungsbezogene Entscheidung. "
                "Die KI trifft hierzu keine verbindliche Entscheidung. "
                "Ihre Anfrage sollte durch einen BKK-Mitarbeiter "
                "geprüft werden."
            ),
            "requires_human": True,
            "status": "ESCALATION_REQUIRED",
        }

    # ---------------------------------------------------------
    # RAG: relevante Informationen aus ChromaDB holen
    # ---------------------------------------------------------

    try:
        embedding = create_embedding(question)

        rag_result = search_documents(
            query_embedding=embedding,
            n_results=3,
        )

        documents = rag_result.get("documents", [[]])[0]
        metadatas = rag_result.get("metadatas", [[]])[0]
        distances = rag_result.get("distances", [[]])[0]

    except Exception:
        documents = []
        metadatas = []
        distances = []

    # ---------------------------------------------------------
    # Kontext für das LLM aufbauen
    # ---------------------------------------------------------

    context_parts = []

    for index, content in enumerate(documents):
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        context_parts.append(
            f"""
Dokument:
{content}

Metadaten:
{metadata}

Distanz:
{distance}
"""
        )

    context = "\n".join(context_parts)

    if not context.strip():
        context = (
            "Es wurden keine passenden internen Dokumente "
            "gefunden."
        )

    # ---------------------------------------------------------
    # LLM Prompt
    # ---------------------------------------------------------

    prompt = f"""
Du bist der digitale Assistent einer gesetzlichen Krankenkasse.

Du unterstützt Versicherte bei allgemeinen Fragen zu:
- Anträgen
- Rechnungen
- Unterlagen
- Bearbeitungsstatus
- allgemeinen Abläufen

WICHTIGE REGELN:

1. Du stellst keine medizinischen Diagnosen.
2. Du triffst keine verbindlichen Leistungs- oder
   Kostenentscheidungen.
3. Verwende die bereitgestellten internen Dokumente
   als Wissensquelle.
4. Erfinde keine Fristen, Beträge, Leistungen,
   Erstattungszusagen, E-Mail-Adressen,
   Postadressen oder Verfahrensregeln.
5. Wenn die internen Dokumente die Frage nicht beantworten,
   sage klar, dass dir hierzu keine zuverlässige Information
   vorliegt.
6. Verwende keine Platzhalter wie [e-mail-Adresse].
7. Bei individuellen oder unklaren Fällen verweise auf
   einen BKK-Mitarbeiter.
8. Antworte auf Deutsch.
9. Antworte verständlich und kurz.

Versicherter:
{patient.first_name} {patient.last_name}

Frage:
{question}

Interne Wissensbasis:
{context}
"""

    provider = LLMProvider()

    answer = provider.generate(prompt)

    return {
        "answer": answer,
        "requires_human": False,
        "status": "ANSWERED",
    }
