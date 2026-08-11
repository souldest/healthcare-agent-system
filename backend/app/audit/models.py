from datetime import datetime, timezone


def create_audit_event(
    case_id: int,
    agent: str,
    action: str,
    status: str,
    result: str | None = None,
) -> dict:
    return {
        "case_id": case_id,
        "agent": agent,
        "action": action,
        "status": status,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
