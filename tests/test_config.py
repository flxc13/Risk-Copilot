from app.core.config import get_settings


def test_poe_settings_read_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("POE_API_KEY", "test-key")
    monkeypatch.setenv("POE_MODEL", "test-model")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.poe_api_key == "test-key"
    assert settings.poe_model == "test-model"

    get_settings.cache_clear()