from __future__ import annotations

from app.core.config import get_settings
from app.data.market_data import MarketDataError, ingest_historical_prices
from app.data.mock_market import get_demo_market_data
from app.data.mock_trades import get_demo_portfolio_by_id
from app.data.portfolio_catalog import get_portfolio, list_portfolios
from app.models.schemas import RiskReport
from app.risk.engine import build_risk_report


def list_available_portfolios() -> list[dict[str, str]]:
    return [
        {
            "portfolio_id": portfolio.portfolio_id,
            "portfolio_name": portfolio.portfolio_name,
            "strategy_style": portfolio.strategy_style,
            "objective": portfolio.objective,
            "benchmark_ticker": portfolio.benchmark_ticker,
        }
        for portfolio in list_portfolios()
    ]


def generate_risk_report(
    use_demo_data: bool = True,
    portfolio_id: str = "core_long_equity",
) -> RiskReport:
    settings = get_settings()
    portfolio = get_portfolio(portfolio_id)
    holdings = get_demo_portfolio_by_id(portfolio.portfolio_id)
    tickers = [holding["ticker"] for holding in holdings if str(holding["ticker"]).upper() != "CASH"]

    if use_demo_data:
        price_frame, benchmark_prices = get_demo_market_data(
            tickers=tickers,
            benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
            periods=settings.demo_lookback_days,
        )
    else:
        try:
            price_frame = ingest_historical_prices(tickers, period="1y")
            benchmark_frame = ingest_historical_prices([portfolio.benchmark_ticker or settings.benchmark_ticker], period="1y")
            benchmark_prices = benchmark_frame[(portfolio.benchmark_ticker or settings.benchmark_ticker).upper()]
        except (MarketDataError, KeyError, IndexError):
            price_frame, benchmark_prices = get_demo_market_data(
                tickers=tickers,
                benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
                periods=settings.demo_lookback_days,
            )

    price_frame = price_frame.copy()
    price_frame["CASH"] = 1.0
    report = build_risk_report(
        price_frame=price_frame,
        holdings=holdings,
        benchmark_prices=benchmark_prices,
        confidence=settings.risk_confidence,
        portfolio_id=portfolio.portfolio_id,
        portfolio_name=portfolio.portfolio_name,
        strategy_style=portfolio.strategy_style,
        portfolio_objective=portfolio.objective,
    )
    return RiskReport.model_validate(report)
