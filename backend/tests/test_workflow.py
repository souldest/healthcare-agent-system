from types import SimpleNamespace
from unittest.mock import patch

from app.workflows.case_workflow import CaseWorkflow


def make_case():
    return SimpleNamespace(
        id=1,
        description="Routine follow-up",
    )


def make_workflow(
    data_quality=None,
    process_analysis=None,
    medical_result=None,
    triage_result=None,
    governance_result=None,
):
    workflow = CaseWorkflow()

    workflow.data_quality_agent.run = lambda case, documents: (
        data_quality
        or {
            "quality_status": "VALID",
        }
    )

    workflow.process_agent.run = lambda case, quality: (
        process_analysis
        or {
            "status": "ANALYZED",
            "next_step": "CONTINUE_PROCESSING",
        }
    )

    workflow.medical_agent.run = lambda db, case_id: (
        medical_result
        or {
            "risk_level": "LOW",
        }
    )

    workflow.triage_agent.run = lambda case: (
        triage_result
        or {
            "priority": "LOW",
        }
    )

    workflow.governance_agent.run = (
        lambda **kwargs: (
            governance_result
            or {
                "decision": "CONTROLLED_CONTINUE",
                "human_review_required": False,
            }
        )
    )

    return workflow


@patch(
    "app.workflows.case_workflow.get_latest_human_review",
    return_value=None,
)
@patch(
    "app.workflows.case_workflow.get_documents_for_case",
    return_value=[],
)
@patch(
    "app.workflows.case_workflow.get_case",
)
@patch(
    "app.workflows.case_workflow.record_event",
)
def test_workflow_completes_when_governance_allows_continue(
    record_event,
    get_case,
    get_documents,
    get_latest_review,
):
    get_case.return_value = make_case()

    workflow = make_workflow(
        governance_result={
            "decision": "CONTROLLED_CONTINUE",
            "human_review_required": False,
        }
    )

    result = workflow.run(
        db=object(),
        case_id=1,
    )

    assert result["status"] == "completed"
    assert result["human_review_required"] is False
    assert result["governance"]["decision"] == "CONTROLLED_CONTINUE"

    get_case.assert_called_once()
    get_documents.assert_called_once()


@patch(
    "app.workflows.case_workflow.get_latest_human_review",
    return_value=None,
)
@patch(
    "app.workflows.case_workflow.get_documents_for_case",
    return_value=[],
)
@patch(
    "app.workflows.case_workflow.get_case",
)
@patch(
    "app.workflows.case_workflow.record_event",
)
def test_workflow_pauses_when_human_review_is_required(
    record_event,
    get_case,
    get_documents,
    get_latest_review,
):
    get_case.return_value = make_case()

    workflow = make_workflow(
        governance_result={
            "decision": "HUMAN_REVIEW",
            "human_review_required": True,
        }
    )

    result = workflow.run(
        db=object(),
        case_id=1,
    )

    assert result["status"] == "waiting_for_human_review"
    assert result["human_review_required"] is True
    assert result["governance"]["decision"] == "HUMAN_REVIEW"
    assert result["human_review"] is None

    assert (
        "Human review required"
        in result["recommendation"]
    )


@patch(
    "app.workflows.case_workflow.get_latest_human_review",
)
@patch(
    "app.workflows.case_workflow.get_documents_for_case",
    return_value=[],
)
@patch(
    "app.workflows.case_workflow.get_case",
)
@patch(
    "app.workflows.case_workflow.record_event",
)
def test_workflow_continues_after_human_review_approval(
    record_event,
    get_case,
    get_documents,
    get_latest_review,
):
    get_case.return_value = make_case()

    approved_review = {
        "status": "APPROVED",
        "reviewer": "human-reviewer",
    }

    get_latest_review.return_value = approved_review

    workflow = make_workflow(
        governance_result={
            "decision": "HUMAN_REVIEW",
            "human_review_required": True,
        }
    )

    result = workflow.run(
        db=object(),
        case_id=1,
    )

    assert result["status"] == "completed"
    assert result["human_review_required"] is False
    assert result["governance"]["decision"] == "APPROVED"
    assert result["governance"]["gate"] == "PASSED"
    assert result["governance"]["human_review"] == approved_review


@patch(
    "app.workflows.case_workflow.get_case",
    return_value=None,
)
def test_workflow_returns_error_for_unknown_case(
    get_case,
):
    workflow = CaseWorkflow()

    result = workflow.run(
        db=object(),
        case_id=999,
    )

    assert result["case_id"] == 999
    assert result["error"] == "Case not found"
