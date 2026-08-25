from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_api_is_reachable():
    response = client.get("/")

    assert response.status_code == 200
