from fastapi.testclient import TestClient

from app.api.main import app


def test_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Risk Advisor Copilot Dashboard" in response.text
    assert "Copilot briefing" not in response.text
    assert "Phase 1 completion" not in response.text
    assert "In-scope function check" not in response.text
    assert "AI Risk Copilot" in response.text
    assert "Report generation" in response.text
    assert "generate-report-button" in response.text
    assert "basel-report-overlay" in response.text
    assert "Basel Capital Monitoring Dashboard" in response.text
    assert "buildBaselDashboardMarkup" in response.text
    assert "Print / PDF" in response.text
    assert '.join("\\n")' in response.text
    assert "Historical stress testing" in response.text
    assert "run-stress-button" in response.text
    assert "stress-scenario-select" in response.text
    assert "renderStressResult" in response.text