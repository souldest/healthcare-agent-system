from types import SimpleNamespace

from app.agents.triage_agent import TriageAgent


def make_case(description):
    return SimpleNamespace(
        id=1,
        description=description,
    )


def test_chest_pain_is_high_priority():
    result = TriageAgent().run(
        make_case("Patient reports chest pain.")
    )

    assert result["priority"] == "HIGH"
    assert "kardiologischen Notfall" in result["reason"]


def test_fever_is_medium_priority():
    result = TriageAgent().run(
        make_case("Patient has fever.")
    )

    assert result["priority"] == "MEDIUM"


def test_non_urgent_case_is_low_priority():
    result = TriageAgent().run(
        make_case("Routine administrative follow-up.")
    )

    assert result["priority"] == "LOW"
