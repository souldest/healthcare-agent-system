import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_risk_analysis_with_mocked_ollama():
    fake_ollama_response = {
        "response": (
            "Hier ist die Management Summary:\n\n"
            "Kunden: 500\n"
            "Gesamtexposure: 309605337,29 EUR"
        )
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def read(self):
            return json.dumps(fake_ollama_response).encode("utf-8")

    with patch(
        "app.main.urllib.request.urlopen",
        return_value=FakeResponse(),
    ):
        response = client.get("/api/ai/risk-analysis")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["generator"] == "ollama"
    assert data["model"] == "llama3.2:1b"

    assert len(data["findings"]) == 3
    assert len(data["recommended_actions"]) == 3


def test_ai_risk_analysis_ollama_error():
    with patch(
        "app.main.ollama_generate",
        side_effect=RuntimeError("Ollama unavailable"),
    ):
        response = client.get("/api/ai/risk-analysis")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "error"
    assert data["generator"] == "ollama"
    assert data["model"] == "llama3.2:1b"
    assert data["analysis"] == (
        "AI-Analyse konnte nicht ausgeführt werden."
    )
    assert "Ollama unavailable" in data["detail"]
