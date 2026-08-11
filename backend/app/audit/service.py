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
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event
