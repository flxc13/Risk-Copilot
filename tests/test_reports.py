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
    assert body["mode"] == "offline_sample_report"
    assert body["title"] == "Basel-Style Risk Capital Charge Report"
    assert "Basel 2.5 IMA Capital Monitoring Statement" in body["report"]
    assert "not** a legal/regulatory filing" in body["report"]
    assert "## Section 3: VaR Model Outputs (99%, 10-day)" in body["report"]
    assert "## Section 4: Backtesting and Multiplier" in body["report"]
    assert "## Section 5: Capital Requirement Calculation" in body["report"]
    assert "Total market risk capital requirement" in body["report"]
    assert body["citations"]
    get_settings.cache_clear()