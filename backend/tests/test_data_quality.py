from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_data_quality():
    response = client.get("/api/data-quality")

    assert response.status_code == 200

    data = response.json()

    assert data["score_pct"] == 99.6
    assert data["total_records"] == 500
    assert data["issue_records"] == 2

    assert len(data["checks"]) > 0

    assert data["note"]
