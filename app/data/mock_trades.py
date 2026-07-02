from __future__ import annotations

from app.data.portfolio_catalog import get_portfolio


def get_demo_portfolio() -> list[dict[str, float | str]]:
    portfolio = get_portfolio()
    return [dict(holding) for holding in portfolio.holdings]


def get_demo_portfolio_by_id(portfolio_id: str) -> list[dict[str, float | str]]:
    portfolio = get_portfolio(portfolio_id)
    return [dict(holding) for holding in portfolio.holdings]
