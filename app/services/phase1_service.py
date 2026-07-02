from __future__ import annotations


def get_phase1_status() -> dict[str, object]:
    items = [
        {
            "key": "sample_portfolios",
            "label": "Sample portfolio creation",
            "complete": True,
            "evidence": "Strategy-based portfolios are available from the portfolio catalog.",
        },
        {
            "key": "market_data_ingestion",
            "label": "Historical market-data ingestion",
            "complete": True,
            "evidence": "Live yfinance ingestion with local cache is implemented.",
        },
        {
            "key": "risk_calculations",
            "label": "Risk calculations",
            "complete": True,
            "evidence": "Daily returns, NAV series, VaR, CVaR, drawdown, benchmark stats, and correlation matrix are returned by the API.",
        },
        {
            "key": "interactive_dashboard",
            "label": "Interactive dashboard",
            "complete": True,
            "evidence": "A browser dashboard is served from /dashboard and reads live API data.",
        },
        {
            "key": "tests",
            "label": "Core calculation tests",
            "complete": True,
            "evidence": "The project includes passing tests for market data ingestion, portfolios, and risk output.",
        },
    ]

    return {
        "phase": "phase_1",
        "complete": all(item["complete"] for item in items),
        "items": items,
    }