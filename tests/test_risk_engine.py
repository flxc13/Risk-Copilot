from app.data.mock_market import get_demo_market_data
from app.data.mock_trades import get_demo_portfolio
from app.data.portfolio_catalog import list_portfolios
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
    assert report["portfolio_value_series"]
    assert report["portfolio_return_series"]
    assert report["drawdown_series"]
    assert report["benchmark_value_series"]
    assert report["correlation_matrix"]
    assert report["tracking_error"] is not None
    assert report["top_holdings"]
    assert report["warnings"] is not None


def test_portfolio_catalog_contains_strategy_baskets() -> None:
    portfolios = list_portfolios()

    assert len(portfolios) >= 3
    assert {portfolio.portfolio_id for portfolio in portfolios} >= {
        "core_long_equity",
        "defensive_income",
        "tactical_macro",
        "event_driven_special_sits",
    }
    assert all(portfolio.risk_budget for portfolio in portfolios)
    assert all(portfolio.pm_desk for portfolio in portfolios)


def test_assess_limits_excludes_cash_from_single_name_warning() -> None:
    warnings = assess_limits(
        historical_var_95=0.01,
        exposures_by_ticker={"CASH": 0.55, "SPY": 0.30, "AAPL": 0.15},
        max_single_name_weight=0.35,
    )

    assert all("CASH" not in warning for warning in warnings)
