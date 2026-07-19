from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.data.market_data import (
    STRESS_WINDOWS,
    MarketDataError,
    StressMarketData,
    ingest_governed_stress_prices,
    ingest_historical_prices,
)
from app.data.mock_market import get_demo_market_data
from app.data.mock_trades import get_demo_portfolio_by_id
from app.data.portfolio_catalog import get_portfolio, list_portfolios
from app.models.schemas import StressRunResult, StressScenarioSummary
from app.risk.stress import run_historical_replay


def _get_stress_portfolio(portfolio_id: str):
    portfolio = get_portfolio(portfolio_id)
    if portfolio.portfolio_id != portfolio_id:
        raise ValueError(f"Unknown portfolio '{portfolio_id}'")
    return portfolio


def list_stress_scenarios(portfolio_id: str) -> list[StressScenarioSummary]:
    portfolio = _get_stress_portfolio(portfolio_id)
    approved = set(portfolio.basel_stress_window_ids)
    scenario_ids = sorted({scenario_id for item in list_portfolios() for scenario_id in item.basel_stress_window_ids})
    return [
        StressScenarioSummary(
            scenario_id=scenario_id,
            start_date=STRESS_WINDOWS[scenario_id][0],
            end_date=STRESS_WINDOWS[scenario_id][1],
            label=STRESS_WINDOWS[scenario_id][2],
            approved_for_portfolio=scenario_id in approved,
        )
        for scenario_id in scenario_ids
    ]


def resolve_stress_scenario(question: str, portfolio_id: str) -> str | None:
    normalized = question.lower()
    if not any(term in normalized for term in ("stress test", "stress testing", "run stress", "historical stress")):
        return None

    aliases = {
        "rates_2022": ("rates", "inflation", "2022 rates"),
        "growth_2022": ("growth", "tech selloff", "long-duration"),
        "covid_2020_12m": ("covid", "pandemic", "2020"),
    }
    portfolio = _get_stress_portfolio(portfolio_id)
    for scenario_id, terms in aliases.items():
        if scenario_id in portfolio.basel_stress_window_ids and any(term in normalized for term in terms):
            return scenario_id
    return portfolio.basel_stress_window_id


def _stress_report(result: dict[str, object]) -> str:
    impacts = result["position_impacts"]
    top_impacts = impacts[:5] if isinstance(impacts, list) else []
    driver_lines = [
        f"- **{row['ticker']}**: ${float(row['pnl']):,.0f} ({float(row['return']):.2%})"
        for row in top_impacts
        if isinstance(row, dict)
    ]
    warnings = result.get("coverage_warnings", [])
    warning_lines = [f"- {warning}" for warning in warnings] if isinstance(warnings, list) and warnings else ["- No market-data coverage warnings."]
    return "\n".join(
        [
            f"# Historical Stress Test: {result['scenario_label']}",
            "",
            f"**Portfolio:** {result['portfolio_name']}",
            f"**Worst replay date:** {result['worst_date']}",
            f"**Worst P&L:** ${float(result['worst_pnl']):,.0f} ({float(result['worst_return']):.2%})",
            f"**Stressed portfolio value:** ${float(result['worst_stressed_value']):,.0f}",
            "",
            "## Largest Loss Contributors",
            *driver_lines,
            "",
            "## Governance and Coverage",
            f"- Scenario ID: `{result['scenario_id']}`",
            f"- Window: {result['scenario_start_date']} to {result['scenario_end_date']}",
            f"- Data mode: {result['data_mode']}",
            f"- Position attribution reconciled: {result['attribution_reconciled']}",
            *warning_lines,
            "",
            "## Interpretation Boundary",
            "- This is a deterministic historical replay of current positions, not a forecast or a regulatory capital calculation.",
            "- Results assume current quantities remain static and do not model liquidity, market impact, intraday trading, financing, or nonlinear optionality beyond observed instrument/proxy returns.",
        ]
    )


def run_stress_test(
    portfolio_id: str,
    scenario_id: str,
    use_demo_data: bool = True,
) -> StressRunResult:
    settings = get_settings()
    portfolio = _get_stress_portfolio(portfolio_id)
    if scenario_id not in portfolio.basel_stress_window_ids:
        raise ValueError(f"Scenario '{scenario_id}' is not approved for portfolio '{portfolio.portfolio_id}'")

    holdings = get_demo_portfolio_by_id(portfolio.portfolio_id)
    tickers = [str(holding["ticker"]).upper() for holding in holdings if str(holding["ticker"]).upper() != "CASH"]
    fallback_warnings: list[str] = []
    if use_demo_data:
        current_prices, _ = get_demo_market_data(
            tickers=tickers,
            benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
            periods=settings.demo_lookback_days,
        )
        data_mode = "demo_current_marks_with_governed_historical_scenario"
    else:
        try:
            current_prices = ingest_historical_prices(tickers, period="1y")
            data_mode = "live_current_marks_with_governed_historical_scenario"
        except MarketDataError as exc:
            current_prices, _ = get_demo_market_data(
                tickers=tickers,
                benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
                periods=settings.demo_lookback_days,
            )
            data_mode = "fallback_demo_current_marks_with_governed_historical_scenario"
            fallback_warnings.append(f"Live current marks unavailable; deterministic demo marks used: {exc}")

    latest_prices = current_prices.ffill().iloc[-1].to_dict()
    try:
        stress_market_data = ingest_governed_stress_prices(tickers, stress_window_id=scenario_id)
    except MarketDataError as exc:
        fallback_prices, _ = get_demo_market_data(
            tickers=tickers,
            benchmark_ticker=portfolio.benchmark_ticker or settings.benchmark_ticker,
            periods=settings.demo_lookback_days,
        )
        _, _, label = STRESS_WINDOWS[scenario_id]
        stress_market_data = StressMarketData(
            prices=fallback_prices,
            window_id=scenario_id,
            label=label,
            proxies_used=[],
            coverage_warnings=[f"Governed historical scenario data unavailable; deterministic demo path used: {exc}"],
            observations=len(fallback_prices.index),
        )
        data_mode = "fallback_demo_current_marks_with_demo_scenario"
    calculation = run_historical_replay(stress_market_data.prices, holdings, latest_prices)
    start_date, end_date, label = STRESS_WINDOWS[scenario_id]
    payload: dict[str, object] = {
        **calculation,
        "run_id": str(uuid4()),
        "generated_at": datetime.now(timezone.utc),
        "portfolio_id": portfolio.portfolio_id,
        "portfolio_name": portfolio.portfolio_name,
        "scenario_id": scenario_id,
        "scenario_label": label,
        "scenario_start_date": start_date,
        "scenario_end_date": end_date,
        "data_mode": data_mode,
        "methodology": "Current marked position values are multiplied by each instrument's cumulative observed return path from the approved historical window; the minimum portfolio value defines the worst replay point.",
        "proxies_used": stress_market_data.proxies_used,
        "coverage_warnings": [*fallback_warnings, *stress_market_data.coverage_warnings],
        "limitations": [
            "Static-balance-sheet replay: quantities and hedges do not change during the scenario.",
            "No liquidity horizon, market impact, funding, margin, or forced-liquidation effects are modeled.",
            "Instrument proxies are applied only under the governed mappings disclosed in this result.",
            "Historical replay is not a forecast and is separate from the legacy Basel 2.5-style capital calculation.",
        ],
    }
    payload["report"] = _stress_report(payload)
    return StressRunResult.model_validate(payload)