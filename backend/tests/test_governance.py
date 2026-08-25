from types import SimpleNamespace

from backend.app.agents.governance_agent import GovernanceAgent


def make_case():
    return SimpleNamespace(id=1)


def run_governance(
    data_quality="VALID",
    priority="LOW",
    risk_level="LOW",
):
    return GovernanceAgent().run(
        case=make_case(),
        data_quality={
            "quality_status": data_quality,
        },
        process_analysis={},
        medical_result={
            "risk_level": risk_level,
        },
        triage_result={
            "priority": priority,
        },
    )


def test_normal_case_can_continue():
    result = run_governance()

    assert result["decision"] == "CONTROLLED_CONTINUE"
    assert result["gate"] == "PASS"
    assert result["human_review_required"] is False
    assert result["rules_triggered"] == []


def test_incomplete_data_requires_human_review():
    result = run_governance(
        data_quality="REVIEW_REQUIRED",
    )

    assert result["decision"] == "HUMAN_REVIEW"
    assert result["gate"] == "ACTIVE"
    assert result["human_review_required"] is True
    assert "DATA_QUALITY_REVIEW" in result["rules_triggered"]


def test_high_triage_priority_requires_human_review():
    result = run_governance(
        priority="HIGH",
    )

    assert result["decision"] == "HUMAN_REVIEW"
    assert result["human_review_required"] is True
    assert "HIGH_RISK" in result["rules_triggered"]


def test_high_medical_risk_requires_human_review():
    result = run_governance(
        risk_level="HIGH",
    )

    assert result["decision"] == "HUMAN_REVIEW"
    assert result["human_review_required"] is True
    assert "MEDICAL_REVIEW_REQUIRED" in result["rules_triggered"]


def test_multiple_governance_rules_are_triggered():
    result = run_governance(
        data_quality="REVIEW_REQUIRED",
        priority="HIGH",
        risk_level="HIGH",
    )

    assert result["decision"] == "HUMAN_REVIEW"
    assert result["human_review_required"] is True

    assert "DATA_QUALITY_REVIEW" in result["rules_triggered"]
    assert "HIGH_RISK" in result["rules_triggered"]
    assert "MEDICAL_REVIEW_REQUIRED" in result["rules_triggered"]
