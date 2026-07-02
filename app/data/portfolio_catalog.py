from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PortfolioDefinition:
    portfolio_id: str
    portfolio_name: str
    strategy_style: str
    objective: str
    benchmark_ticker: str
    holdings: tuple[dict[str, float | str], ...]


PORTFOLIO_CATALOG: dict[str, PortfolioDefinition] = {
    "core_long_equity": PortfolioDefinition(
        portfolio_id="core_long_equity",
        portfolio_name="Core Long Equity",
        strategy_style="Quality growth / long-only",
        objective="Compound capital with high-conviction large-cap equity exposure and a modest cash buffer.",
        benchmark_ticker="SPY",
        holdings=(
            {"ticker": "AAPL", "quantity": 30, "average_cost": 175.0, "asset_class": "Equity"},
            {"ticker": "MSFT", "quantity": 24, "average_cost": 330.0, "asset_class": "Equity"},
            {"ticker": "NVDA", "quantity": 10, "average_cost": 420.0, "asset_class": "Equity"},
            {"ticker": "AMZN", "quantity": 20, "average_cost": 145.0, "asset_class": "Equity"},
            {"ticker": "SPY", "quantity": 12, "average_cost": 460.0, "asset_class": "ETF"},
            {"ticker": "CASH", "quantity": 12000.0, "average_cost": 1.0, "asset_class": "Cash"},
        ),
    ),
    "defensive_income": PortfolioDefinition(
        portfolio_id="defensive_income",
        portfolio_name="Defensive Income",
        strategy_style="Capital preservation / income",
        objective="Prioritize drawdown control and steadier returns through defensive equities, bonds, gold, and cash.",
        benchmark_ticker="SPY",
        holdings=(
            {"ticker": "MSFT", "quantity": 14, "average_cost": 330.0, "asset_class": "Equity"},
            {"ticker": "SPY", "quantity": 8, "average_cost": 460.0, "asset_class": "ETF"},
            {"ticker": "TLT", "quantity": 42, "average_cost": 92.0, "asset_class": "Bond ETF"},
            {"ticker": "GLD", "quantity": 22, "average_cost": 185.0, "asset_class": "Commodity"},
            {"ticker": "CASH", "quantity": 20000.0, "average_cost": 1.0, "asset_class": "Cash"},
        ),
    ),
    "tactical_macro": PortfolioDefinition(
        portfolio_id="tactical_macro",
        portfolio_name="Tactical Macro",
        strategy_style="Macro / regime rotation",
        objective="Rotate capital between risk assets and diversifiers when macro conditions shift.",
        benchmark_ticker="SPY",
        holdings=(
            {"ticker": "NVDA", "quantity": 8, "average_cost": 420.0, "asset_class": "Equity"},
            {"ticker": "AAPL", "quantity": 12, "average_cost": 175.0, "asset_class": "Equity"},
            {"ticker": "TLT", "quantity": 60, "average_cost": 92.0, "asset_class": "Bond ETF"},
            {"ticker": "GLD", "quantity": 28, "average_cost": 185.0, "asset_class": "Commodity"},
            {"ticker": "CASH", "quantity": 25000.0, "average_cost": 1.0, "asset_class": "Cash"},
        ),
    ),
}


def list_portfolios() -> list[PortfolioDefinition]:
    return list(PORTFOLIO_CATALOG.values())


def get_portfolio(portfolio_id: str | None = None) -> PortfolioDefinition:
    if portfolio_id and portfolio_id in PORTFOLIO_CATALOG:
        return PORTFOLIO_CATALOG[portfolio_id]
    return PORTFOLIO_CATALOG["core_long_equity"]
