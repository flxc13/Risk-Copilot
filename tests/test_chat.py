from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import get_settings


def test_chat_endpoint_returns_offline_copilot_answer_without_key(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "question": "What is the main downside risk?",
            "portfolio_id": "core_long_equity",
            "use_demo_data": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "offline_fallback"
    assert "historical VaR" in body["answer"]
    assert body["citations"]
    get_settings.cache_clear()