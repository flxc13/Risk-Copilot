from fastapi.testclient import TestClient

from app.api.main import app


def test_dashboard_page_renders() -> None:
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Risk Advisor Copilot Dashboard" in response.text
    assert 'href="/regulatory-intelligence"' in response.text
    assert "AI-Enhanced Risk Command Center" in response.text
    assert "Risk Operations Console" not in response.text
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
    assert "stress-data-source" in response.text
    assert "stressDataSourceLabel" in response.text
    assert "heroFloat" in response.text
    assert "telemetryBreathe" in response.text
    assert "launcherFloat" in response.text
    assert "brandCorePulse" in response.text
    assert "commandSweep" not in response.text
    assert "particleDrift" in response.text
    assert "z-index: 2" in response.text
    assert "sectionSignal" in response.text
    assert "--accent: #c7c9cc" in response.text
    assert "--bg: #030303" in response.text
    assert "const chartTheme" in response.text
    assert 'portfolio: "#2962ff"' in response.text
    assert 'positive: "#26a69a"' in response.text
    assert 'loss: "#ef5350"' in response.text