import pandas as pd

from app.data.market_data import StressMarketData
from app.data.mock_market import get_demo_market_data
from app.data.mock_trades import get_demo_portfolio
from app.data.portfolio_catalog import list_portfolios
from app.services.risk_service import generate_risk_report
from app.risk.engine import build_risk_report
from app.risk.limits import assess_limits


def test_build_risk_report_contains_expected_fields() -> None:
    portfolio = get_demo_portfolio()
    tickers = [holding["ticker"] for holding in portfolio if holding["ticker"] != "CASH"]
    price_frame, benchmark_prices = get_demo_market_data(tickers=tickers, benchmark_ticker="SPY", periods=120)
    price_frame["CASH"] = 1.0

    report = build_risk_report(price_frame=price_frame, holdings=portfolio, benchmark_prices=benchmark_prices)

    assert report["total_value"] > 0
    assert 0 <= report["historical_var_95"] < 1
    assert 0 <= report["expected_shortfall_95"] < 1
    assert 0 <= report["basel_var_99_10d"] < 1
    assert 0 <= report["basel_stressed_var_99_10d"] < 1
    assert report["basel_stress_window_id"]
    assert report["basel_stress_window"]
    assert report["basel_stress_data_mode"]
    assert report["basel_stress_methodology"]
    assert isinstance(report["basel_stress_proxies_used"], list)
    assert isinstance(report["basel_svar_governance_warnings"], list)
    assert report["basel_backtesting_observations"] > 0
    assert report["basel_backtesting_zone"] in {"green", "yellow", "red"}
    assert report["basel_capital_multiplier"] >= 3.0
    assert report["basel_total_capital_charge"] >= 0
    assert report["portfolio_value_series"]
    assert report["portfolio_return_series"]
    assert report["drawdown_series"]
    assert report["benchmark_value_series"]
    assert report["correlation_matrix"]
    assert report["tracking_error"] is not None
    assert report["top_holdings"]
    assert report["warnings"] is not None


def test_build_risk_report_uses_distinct_stress_price_frame_for_svar() -> None:
    portfolio = get_demo_portfolio()
    tickers = [holding["ticker"] for holding in portfolio if holding["ticker"] != "CASH"]
    price_frame, benchmark_prices = get_demo_market_data(tickers=tickers, benchmark_ticker="SPY", periods=180)
    stress_frame = price_frame.copy()
    stress_frame.iloc[40:] = stress_frame.iloc[40:] * 0.90
    stress_frame.iloc[41:] = stress_frame.iloc[41:] * 0.82
    stress_frame.iloc[42:] = stress_frame.iloc[42:] * 0.74
    stress_frame.iloc[43:] = stress_frame.iloc[43:] * 0.66
    price_frame["CASH"] = 1.0
    stress_frame["CASH"] = 1.0

    report = build_risk_report(
        price_frame=price_frame,
        holdings=portfolio,
        benchmark_prices=benchmark_prices,
        stress_price_frame=stress_frame,
        stress_window_id="unit_test_window",
        stress_window_label="Unit-test real stress proxy",
        stress_data_mode="test_stress_window",
        stress_methodology="Unit-test approved stress methodology.",
        stress_proxies_used=[{"ticker": "AAPL", "proxy_ticker": "SPY", "return_multiplier": 1.0, "reason": "test"}],
    )

    assert report["basel_stressed_var_99_10d"] > report["basel_var_99_10d"]
    assert report["basel_stress_window_id"] == "unit_test_window"
    assert report["basel_stress_window"] == "Unit-test real stress proxy"
    assert report["basel_stress_data_mode"] == "test_stress_window"
    assert report["basel_stress_proxies_used"][0]["proxy_ticker"] == "SPY"


def test_portfolio_catalog_contains_strategy_baskets() -> None:
    portfolios = list_portfolios()

    assert len(portfolios) >= 3
    assert {portfolio.portfolio_id for portfolio in portfolios} >= {
        "core_long_equity",
        "defensive_income",
        "tactical_macro",
        "event_driven_special_sits",
        "high_octane_trading",
    }
    assert all(portfolio.risk_budget for portfolio in portfolios)
    assert all(portfolio.pm_desk for portfolio in portfolios)
    assert all(portfolio.basel_stress_window_id for portfolio in portfolios)
    assert all(portfolio.basel_stress_methodology for portfolio in portfolios)


def test_live_risk_report_evaluates_approved_stress_window_candidates(monkeypatch) -> None:
    stress_window_ids: list[str] = []
    dates = pd.date_range("2026-01-01", periods=90, freq="B")

    def price_frame_for(tickers: list[str]) -> pd.DataFrame:
        return pd.DataFrame(
            {ticker.upper(): [100.0 + index for index, _ in enumerate(dates)] for ticker in tickers if ticker.upper() != "CASH"},
            index=dates,
        )

    def fake_ingest_historical_prices(tickers, period="1y", **kwargs):
        return price_frame_for([str(ticker) for ticker in tickers])

    def fake_ingest_governed_stress_prices(tickers, stress_window_id, **kwargs):
        stress_window_ids.append(stress_window_id)
        stress_prices = price_frame_for([str(ticker) for ticker in tickers])
        return StressMarketData(
            prices=stress_prices,
            window_id=stress_window_id,
            label="Unit-test approved stress window",
            proxies_used=[],
            coverage_warnings=[],
            observations=len(stress_prices),
        )

    monkeypatch.setattr("app.services.risk_service.ingest_historical_prices", fake_ingest_historical_prices)
    monkeypatch.setattr("app.services.risk_service.ingest_governed_stress_prices", fake_ingest_governed_stress_prices)

    report = generate_risk_report(use_demo_data=False, portfolio_id="defensive_income")

    assert stress_window_ids == ["rates_2022", "covid_2020_12m"]
    assert report.basel_stress_window_id == "rates_2022"
    assert report.basel_stress_candidate_window_ids == ["rates_2022", "covid_2020_12m"]
    assert report.basel_stress_data_mode == "approved_real_market_stress_window"


def test_high_octane_portfolio_has_elevated_basel_capital_charge() -> None:
    core_report = generate_risk_report(use_demo_data=True, portfolio_id="core_long_equity")
    high_risk_report = generate_risk_report(use_demo_data=True, portfolio_id="high_octane_trading")

    assert high_risk_report.portfolio_name == "High-Octane Levered Trading Book"
    assert high_risk_report.basel_total_capital_charge > core_report.basel_total_capital_charge
    assert high_risk_report.basel_total_capital_charge / high_risk_report.total_value > 0.75
    assert high_risk_report.basel_var_99_10d > core_report.basel_var_99_10d


def test_assess_limits_excludes_cash_from_single_name_warning() -> None:
    warnings = assess_limits(
        historical_var_95=0.01,
        exposures_by_ticker={"CASH": 0.55, "SPY": 0.30, "AAPL": 0.15},
        max_single_name_weight=0.35,
    )

    assert all("CASH" not in warning for warning in warnings)
