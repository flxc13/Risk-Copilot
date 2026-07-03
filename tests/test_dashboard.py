from fastapi.testclient import TestClient

from app.api.main import app


def test_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Risk Advisor Copilot Dashboard" in response.text
    assert "Copilot briefing" in response.text
    assert "Phase 1 completion" not in response.text
    assert "In-scope function check" not in response.text
    assert "AI Risk Copilot" in response.text