from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_risk_overview():
    response = client.get("/api/risk/overview")

    assert response.status_code == 200

    data = response.json()

    assert data["summary"]["customers"] == 500
    assert data["summary"]["high_risk_customers"] == 52
    assert data["summary"]["default_rate_pct"] == "3.00"
    assert data["summary"]["total_exposure"] == "309605337.29"

    assert len(data["distribution"]) == 3
