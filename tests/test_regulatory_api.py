from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import get_settings


def test_regulatory_updates_and_refresh_fallback(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    updates_response = client.get("/api/regulatory/updates?jurisdiction=HK")
    refresh_response = client.post("/api/regulatory/refresh")

    assert updates_response.status_code == 200
    assert updates_response.json()
    assert all(item["jurisdiction"] == "HK" for item in updates_response.json())
    assert refresh_response.status_code == 200
    assert refresh_response.json()["mode"] == "seed_fallback"
    get_settings.cache_clear()


def test_newsletter_generation_is_saved(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    generated = client.post("/api/regulatory/newsletters/generate")
    history = client.get("/api/regulatory/newsletters")

    assert generated.status_code == 200
    assert generated.json()["generation_mode"] == "editorial_fallback"
    assert "not legal advice" in generated.json()["disclaimer"]
    assert generated.json()["id"] in {issue["id"] for issue in history.json()}
    get_settings.cache_clear()


def test_schedule_is_an_explicit_placeholder() -> None:
    response = TestClient(app).get("/api/regulatory/schedule")

    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["frequency"] == "weekly"


def test_regulatory_intelligence_page_renders() -> None:
    response = TestClient(app).get("/regulatory-intelligence")

    assert response.status_code == 200
    assert "Capital Markets Intelligence" in response.text
    assert "Update intelligence" in response.text
    assert "Generate weekly issue" in response.text
    assert 'href="/dashboard"' in response.text
    assert "DOMPurify.sanitize" in response.text
    assert 'id="workspace-divider"' in response.text
    assert 'role="separator"' in response.text
    assert "startWorkspaceResize" in response.text
    assert 'id="print-button"' in response.text
    assert "printNewsletter" in response.text
    assert "@media print" in response.text
    assert "@page { margin: 0; }" in response.text
    assert 'document.title = ""' in response.text