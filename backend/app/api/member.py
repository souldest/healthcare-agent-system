from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.patient import Patient
from app.models.case import Case
from app.llm.provider import LLMProvider


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
3. Erfinde keine Fristen, Beträge, Leistungen,
   Erstattungszusagen oder Verfahrensregeln.
4. Wenn dir eine Information nicht zuverlässig vorliegt,
   sage das offen.
5. Bei individuellen oder unklaren Fällen verweise
   auf einen BKK-Mitarbeiter.
6. Antworte auf Deutsch.
7. Antworte verständlich und kurz.

Versicherter:
{patient.first_name} {patient.last_name}

Frage:
{question}
"""

    provider = LLMProvider()

    answer = provider.generate(prompt)

    return {
        "answer": answer,
        "requires_human": False,
        "status": "ANSWERED",
    }
