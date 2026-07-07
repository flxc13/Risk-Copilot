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
    assert "not** an FRTB-SA, FRTB-IMA, or regulatory capital submission" in body["report"]
    assert "## FRTB-SA Proxy: Sensitivities-Based Method (SBM)" in body["report"]
    assert "## FRTB-SA Proxy: Default Risk Charge (DRC)" in body["report"]
    assert "## FRTB-SA Proxy: Residual Risk Add-On (RRAO)" in body["report"]
    assert "## Capital Stack and Binding Charge" in body["report"]
    assert body["citations"]
    get_settings.cache_clear()