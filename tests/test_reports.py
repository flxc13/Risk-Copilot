from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import get_settings


def test_generate_report_returns_fallback_markdown_without_key(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/reports/generate",
        json={
            "portfolio_id": "core_long_equity",
            "use_demo_data": True,
            "report_type": "morning_note",
            "audience": "PM",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "offline_sample_report"
    assert body["title"] == "Morning Risk Report"
    assert "# Morning Risk Report" in body["report"]
    assert "## Risk Snapshot" in body["report"]
    assert body["citations"]
    get_settings.cache_clear()


def test_generate_basel_style_report_returns_capital_charge_section(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/reports/generate",
        json={
            "portfolio_id": "core_long_equity",
            "use_demo_data": True,
            "report_type": "basel_simplified_capital",
            "audience": "Risk Control",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "deterministic_basel_dashboard"
    assert body["title"] == "Basel-Style Risk Capital Charge Report"
    assert "Legacy Basel 2.5 IMA-Style Capital Monitoring" in body["report"]
    assert "not** a legal/regulatory filing" in body["report"]
    assert "## At a Glance" in body["report"]
    assert "## VaR Model Outputs (99%, 10-day)" in body["report"]
    assert "## Backtesting and Multiplier" in body["report"]
    assert "## Capital Stack" in body["report"]
    assert "## Stress Data Governance" in body["report"]
    assert "Approved Stressed VaR window ID" in body["report"]
    assert "Total market risk capital requirement" in body["report"]
    assert body["dashboard"]["status"]["traffic_light"] == "insufficient"
    assert len(body["dashboard"]["headline_metrics"]) == 4
    assert body["dashboard"]["capital_stack"][0]["status"] == "calculated"
    assert body["dashboard"]["capital_stack"][2]["status"] == "not_implemented"
    assert body["dashboard"]["calculation_evidence"][0]["formula"]
    assert body["dashboard"]["stress_governance"]["selected_window_id"]
    assert body["dashboard"]["limitations"]
    assert "not FRTB IMA" in body["dashboard"]["framework"]
    assert body["citations"]
    get_settings.cache_clear()