from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_risk_analysis():
    response = client.get("/api/ai/risk-analysis")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["generator"] == "ollama"
    assert data["model"]

    assert len(data["findings"]) == 3
    assert len(data["recommended_actions"]) == 3

    assert data["data_quality"]["score_pct"] == 99.6
    assert data["data_quality"]["issue_records"] == 2
    assert data["data_quality"]["failed_checks"] == 1
