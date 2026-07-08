from __future__ import annotations

from app.core.config import get_settings
from app.data.market_data import MarketDataError, StressMarketData, ingest_governed_stress_prices, ingest_historical_prices
from app.data.mock_market import get_demo_market_data
from app.data.mock_trades import get_demo_portfolio_by_id
from app.data.portfolio_catalog import PortfolioDefinition, get_portfolio, list_portfolios
from app.models.schemas import RiskReport
from app.risk.engine import build_risk_report, portfolio_returns_from_current_values
from app.risk.var import basel_historical_var


def _select_governed_stress_market_data(
    tickers: list[str],
    holdings: list[dict[str, float | str]],
    portfolio: PortfolioDefinition,
    latest_prices: dict[str, float],
) -> StressMarketData:
    candidates: list[tuple[float, StressMarketData]] = []
    candidate_ids = portfolio.basel_stress_window_ids or (portfolio.basel_stress_window_id,)
    last_error: MarketDataError | None = None

    for stress_window_id in candidate_ids:
        try:
            stress_market_data = ingest_governed_stress_prices(tickers, stress_window_id=stress_window_id)
            stress_returns = portfolio_returns_from_current_values(stress_market_data.prices, holdings, latest_prices)
            stress_var = basel_historical_var(stress_returns, confidence=0.99, horizon_days=10)
            candidates.append((stress_var, stress_market_data))
        except MarketDataError as exc:
            last_error = exc

    if not candidates:
        raise last_error or MarketDataError("No approved stress candidate windows returned usable market data")

    return max(candidates, key=lambda candidate: candidate[0])[1]


def list_available_portfolios() -> list[dict[str, str]]:
    return [
        {
            "portfolio_id": portfolio.portfolio_id,
            "portfolio_name": portfolio.portfolio_name,
            "strategy_style": portfolio.strategy_style,
            "objective": portfolio.objective,
            "benchmark_ticker": portfolio.benchmark_ticker,
            "risk_budget": portfolio.risk_budget,
            "target_net_exposure": portfolio.target_net_exposure,
            "target_gross_exposure": portfolio.target_gross_exposure,
            "pm_desk": portfolio.pm_desk,
            "basel_stress_window_id": portfolio.basel_stress_window_id,
            "basel_stress_window_ids": ",".join(portfolio.basel_stress_window_ids),
            "basel_stress_methodology": portfolio.basel_stress_methodology,
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
        stress_price_frame = None
        stress_window_label = "Recent demo sample tail-risk window"
        stress_data_mode = "demo_sample_window"
        stress_window_id = "demo_sample_window"
        stress_candidate_window_ids = []
        stress_methodology = "Demo mode uses the deterministic sample tail-risk selector instead of live governed calibration."
        stress_proxies_used: list[dict[str, float | str]] = []
        stress_coverage_warnings: list[str] = []
    else:
        try:
            price_frame = ingest_historical_prices(tickers, period="1y")
            latest_prices = price_frame.ffill().iloc[-1].to_dict()
            stress_market_data = _select_governed_stress_market_data(tickers, holdings, portfolio, latest_prices)
            stress_price_frame = stress_market_data.prices
            stress_window_label = stress_market_data.label
            stress_data_mode = "approved_real_market_stress_window"
            stress_window_id = stress_market_data.window_id
            stress_candidate_window_ids = list(portfolio.basel_stress_window_ids)
            stress_methodology = portfolio.basel_stress_methodology
            stress_proxies_used = stress_market_data.proxies_used
            stress_coverage_warnings = stress_market_data.coverage_warnings
            benchmark_frame = ingest_historical_prices([portfolio.benchmark_ticker or settings.benchmark_ticker], period="1y")
            benchmark_prices = benchmark_frame[(portfolio.benchmark_ticker or settings.benchmark_ticker).upper()]
        except (MarketDataError, KeyError, IndexError):
            price_frame, benchmark_prices = get_demo_market_data(
                tickers=tickers,
                benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
                periods=settings.demo_lookback_days,
            )
            stress_price_frame = None
            stress_window_label = "Recent demo sample tail-risk window"
            stress_data_mode = "fallback_demo_sample_window"
            stress_window_id = "fallback_demo_sample_window"
            stress_candidate_window_ids = list(portfolio.basel_stress_window_ids)
            stress_methodology = "Live governed stress data was unavailable; report fell back to deterministic demo stress selection."
            stress_proxies_used = []
            stress_coverage_warnings = ["Live governed stress data was unavailable; fallback demo stress window used."]

    price_frame = price_frame.copy()
    price_frame["CASH"] = 1.0
    report = build_risk_report(
        price_frame=price_frame,
        holdings=holdings,
        benchmark_prices=benchmark_prices,
        stress_price_frame=stress_price_frame,
        stress_window_label=stress_window_label,
        stress_data_mode=stress_data_mode,
        stress_window_id=stress_window_id,
        stress_candidate_window_ids=stress_candidate_window_ids,
        stress_methodology=stress_methodology,
        stress_proxies_used=stress_proxies_used,
        stress_coverage_warnings=stress_coverage_warnings,
        confidence=settings.risk_confidence,
        portfolio_id=portfolio.portfolio_id,
        portfolio_name=portfolio.portfolio_name,
        strategy_style=portfolio.strategy_style,
        portfolio_objective=portfolio.objective,
    )
    return RiskReport.model_validate(report)
