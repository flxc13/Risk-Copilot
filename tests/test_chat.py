from types import SimpleNamespace

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


def test_chat_executes_stress_tool_without_key_as_explicit_fallback(monkeypatch) -> None:
    monkeypatch.delenv("POE_API_KEY", raising=False)
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "question": "Run the approved growth stress test and give me the report.",
            "portfolio_id": "core_long_equity",
            "use_demo_data": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "offline_tool_fallback"
    assert body["tool_calls"][0]["name"] == "run_stress_test"
    assert body["stress_result"]["scenario_id"] == "growth_2022"
    assert body["stress_result"]["attribution_reconciled"] is True
    assert "Historical Stress Test" in body["answer"]
    get_settings.cache_clear()


def test_chat_calls_llm_then_executes_requested_stress_tool(monkeypatch) -> None:
    monkeypatch.setenv("POE_API_KEY", "unit-test-key")
    get_settings.cache_clear()
    calls: list[dict[str, object]] = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                return SimpleNamespace(
                    id="response-1",
                    output_text="",
                    output=[
                        SimpleNamespace(
                            type="function_call",
                            name="run_stress_test",
                            arguments='{"scenario_id":"growth_2022"}',
                            call_id="call-1",
                        )
                    ],
                )
            return SimpleNamespace(
                id="response-2",
                output_text="## Executive readout\nThe governed growth stress was executed successfully.",
                output=[],
            )

    class FakeClient:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "question": "Use your tool to run the growth stress and report the result.",
            "portfolio_id": "core_long_equity",
            "use_demo_data": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "poe_tool_execution"
    assert body["tool_calls"][0]["name"] == "run_stress_test"
    assert body["stress_result"]["scenario_id"] == "growth_2022"
    assert body["answer"].startswith("## Executive readout")
    assert len(calls) == 2
    assert calls[0]["tools"][0]["name"] == "run_stress_test"
    assert "previous_response_id" not in calls[1]
    assert calls[1]["input"][0]["role"] == "user"
    assert calls[1]["input"][1]["type"] == "function_call"
    assert calls[1]["input"][2]["type"] == "function_call_output"
    assert '"attribution_reconciled": true' in calls[1]["input"][2]["output"]
    get_settings.cache_clear()