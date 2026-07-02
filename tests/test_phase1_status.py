from fastapi.testclient import TestClient

from app.api.main import app


def test_phase1_status_endpoint_reports_complete() -> None:
    client = TestClient(app)
    response = client.get("/api/phase1/status")

    assert response.status_code == 200
    body = response.json()
    assert body["complete"] is True
    assert body["items"]
    assert all(item["complete"] for item in body["items"])