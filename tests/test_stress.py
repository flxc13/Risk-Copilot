import pandas as pd
from fastapi.testclient import TestClient

from app.api.main import app
from app.risk.stress import run_historical_replay


def test_historical_replay_reconciles_worst_loss_attribution() -> None:
    dates = pd.date_range("2020-02-19", periods=3, freq="B")
    prices = pd.DataFrame(
        {
            "EQUITY": [100.0, 80.0, 90.0],
            "HEDGE": [100.0, 115.0, 105.0],
        },
        index=dates,
    )
    holdings = [
        {"ticker": "EQUITY", "quantity": 10.0, "asset_class": "Equity", "risk_bucket": "Beta"},
        {"ticker": "HEDGE", "quantity": 2.0, "asset_class": "ETF", "risk_bucket": "Hedge"},
        {"ticker": "CASH", "quantity": 500.0, "asset_class": "Cash", "risk_bucket": "Liquidity"},
    ]

    result = run_historical_replay(
        stress_prices=prices,
        holdings=holdings,
        latest_prices={"EQUITY": 120.0, "HEDGE": 50.0},
    )

    assert result["worst_date"] == "2020-02-20"
    assert result["worst_pnl"] == -225.0
    assert result["worst_stressed_value"] == 1575.0
    assert result["attribution_reconciled"] is True
    assert sum(float(row["pnl"]) for row in result["position_impacts"]) == result["worst_pnl"]
    cash = next(row for row in result["position_impacts"] if row["ticker"] == "CASH")
    assert cash["pnl"] == 0.0


def test_manual_stress_endpoint_returns_governed_reconciled_run() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/stress/runs",
        json={
            "portfolio_id": "core_long_equity",
            "scenario_id": "growth_2022",
            "use_demo_data": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scenario_id"] == "growth_2022"
    assert body["data_mode"] == "demo_current_marks_with_governed_historical_scenario"
    assert body["worst_pnl"] < 0
    assert body["attribution_reconciled"] is True
    assert sum(row["pnl"] for row in body["position_impacts"]) == body["worst_pnl"]
    assert body["report"].startswith("# Historical Stress Test")


def test_stress_endpoint_rejects_unapproved_portfolio_scenario() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/stress/runs",
        json={
            "portfolio_id": "defensive_income",
            "scenario_id": "growth_2022",
            "use_demo_data": True,
        },
    )

    assert response.status_code == 422
    assert "not approved" in response.json()["detail"]


def test_scenario_catalog_marks_portfolio_approvals() -> None:
    client = TestClient(app)

    response = client.get("/api/stress/scenarios", params={"portfolio_id": "defensive_income"})

    assert response.status_code == 200
    scenarios = {row["scenario_id"]: row for row in response.json()["scenarios"]}
    assert scenarios["rates_2022"]["approved_for_portfolio"] is True
    assert scenarios["growth_2022"]["approved_for_portfolio"] is False