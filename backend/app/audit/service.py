import json
from pathlib import Path

from app.audit.models import create_audit_event


AUDIT_LOG = Path(__file__).resolve().parents[2] / "audit.log"


def record_event(
    case_id: int,
    agent: str,
    action: str,
    status: str,
    result: str | None = None,
) -> dict:
    event = create_audit_event(
        case_id=case_id,
        agent=agent,
        action=action,
        status=status,
        result=result,
    )

    with AUDIT_LOG.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(event, ensure_ascii=False) + "\n"
        )

    return event


def get_case_history(case_id: int) -> list[dict]:
    if not AUDIT_LOG.exists():
        return []

    history = []

    with AUDIT_LOG.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("case_id") == case_id:
                history.append(event)

    return history


def record_human_review(
    case_id: int,
    decision: str,
    reviewer: str = "Human Reviewer",
    comment: str | None = None,
) -> dict:
    normalized_decision = decision.upper().strip()

    allowed_decisions = {
        "APPROVED",
        "REJECTED",
        "REQUEST_CHANGES",
    }

    if normalized_decision not in allowed_decisions:
        raise ValueError(
            "Invalid human review decision. "
            "Allowed: APPROVED, REJECTED, REQUEST_CHANGES"
        )

    # ---------------------------------------------------------
    # Idempotenz:
    # Dieselbe Review-Entscheidung darf nicht mehrfach
    # für denselben Case in den Audit-Trail geschrieben werden.
    #
    # Dadurch erzeugt ein doppelter Frontend-Request oder ein
    # erneuter Klick auf denselben Review-Button kein weiteres
    # identisches HUMAN_REVIEW_DECISION Event.
    # ---------------------------------------------------------

    history = get_case_history(case_id)

    for event in reversed(history):

        if event.get("action") != "HUMAN_REVIEW_DECISION":
            continue

        existing_status = (
            str(event.get("status", ""))
            .upper()
            .strip()
        )

        if existing_status == normalized_decision:

            return event

        # Eine andere Entscheidung darf eine neue fachliche
        # Review-Entscheidung darstellen.
        break

    return record_event(
        case_id=case_id,
        agent=reviewer,
        action="HUMAN_REVIEW_DECISION",
        status=normalized_decision,
        result=comment or "Fachliche Prüfung abgeschlossen.",
    )


def get_latest_human_review(case_id: int) -> dict | None:
    history = get_case_history(case_id)

    for event in reversed(history):
        if event.get("action") == "HUMAN_REVIEW_DECISION":
            return event

    return None
