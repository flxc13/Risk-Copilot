from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import sqrt

import numpy as np
import pandas as pd

from app.risk.drivers import build_driver_summary
from app.risk.exposure import exposure_by_asset_class, exposure_by_ticker, top_holdings
from app.risk.limits import assess_limits
from app.risk.var import (
    annualized_volatility,
    expected_shortfall,
    historical_var,
    parametric_var,
    rolling_var,
    rolling_volatility,
    sharpe_ratio,
)


def _holdings_frame(holdings: Sequence[Mapping[str, float | str]]) -> pd.DataFrame:
    rows = []
    for holding in holdings:
        rows.append(
            {
                "ticker": str(holding["ticker"]).upper(),
                "quantity": float(holding["quantity"]),
                "average_cost": float(holding.get("average_cost", 0.0)),
                "asset_class": str(holding.get("asset_class", "Other")),
            }
        )
    return pd.DataFrame(rows)


def _portfolio_value_series(
    price_frame: pd.DataFrame,
    holdings: Sequence[Mapping[str, float | str]],
) -> tuple[pd.Series, dict[str, float]]:
    holdings_frame = _holdings_frame(holdings)
    if holdings_frame.empty:
        empty = pd.Series(dtype=float)
        return empty, {}

    aligned_prices = price_frame.copy()
    for ticker in holdings_frame["ticker"]:
        if ticker not in aligned_prices.columns:
            aligned_prices[ticker] = 1.0 if ticker == "CASH" else np.nan

    aligned_prices = aligned_prices.reindex(columns=holdings_frame["ticker"].tolist()).ffill().bfill()
    missing_columns = [column for column in aligned_prices.columns if aligned_prices[column].isna().all()]
    missing_non_cash = [column for column in missing_columns if column != "CASH"]
    if missing_non_cash:
        raise ValueError(f"Missing market prices for: {', '.join(missing_non_cash)}")
    if "CASH" in aligned_prices.columns:
        aligned_prices["CASH"] = 1.0

    quantities = holdings_frame.set_index("ticker")["quantity"]
    portfolio_values = aligned_prices.mul(quantities, axis=1).sum(axis=1)
    latest_prices = aligned_prices.ffill().iloc[-1].to_dict()
    return portfolio_values, latest_prices


def maximum_drawdown(value_series: pd.Series) -> float:
    if value_series.empty:
        return 0.0
    running_max = value_series.cummax()
    drawdowns = value_series / running_max - 1.0
    return float(abs(drawdowns.min()))


def build_risk_report(
    price_frame: pd.DataFrame,
    holdings: Sequence[Mapping[str, float | str]],
    benchmark_prices: pd.Series | None = None,
    confidence: float = 0.95,
    portfolio_id: str = "core_long_equity",
    portfolio_name: str = "Demo Portfolio",
    strategy_style: str = "",
    portfolio_objective: str = "",
) -> dict[str, object]:
    portfolio_values, latest_prices = _portfolio_value_series(price_frame, holdings)
    if portfolio_values.empty:
        raise ValueError("Portfolio values could not be calculated")

    portfolio_returns = portfolio_values.pct_change().dropna()
    latest_value = float(portfolio_values.iloc[-1])
    first_value = float(portfolio_values.iloc[0])
    total_return = 0.0 if first_value == 0 else latest_value / first_value - 1.0
    daily_return = float(portfolio_returns.iloc[-1]) if not portfolio_returns.empty else 0.0
    volatility = float(portfolio_returns.std(ddof=0)) if not portfolio_returns.empty else 0.0
    annualized = annualized_volatility(portfolio_returns)
    historical = historical_var(portfolio_returns, confidence=confidence)
    parametric = parametric_var(portfolio_returns, confidence=confidence)
    shortfall = expected_shortfall(portfolio_returns, confidence=confidence)
    drawdown = maximum_drawdown(portfolio_values)
    sharpe = sharpe_ratio(portfolio_returns)
    exposure_ticker = exposure_by_ticker(holdings, latest_prices)
    exposure_asset_class = exposure_by_asset_class(holdings, latest_prices)
    drivers = build_driver_summary(holdings, latest_prices)
    top_rows = top_holdings(holdings, latest_prices)

    beta_vs_benchmark = None
    if benchmark_prices is not None:
        benchmark_returns = benchmark_prices.pct_change().dropna()
        if not benchmark_returns.empty and not portfolio_returns.empty:
            aligned = pd.concat(
                [portfolio_returns.rename("portfolio"), benchmark_returns.rename("benchmark")],
                axis=1,
                join="inner",
            ).dropna()
            if len(aligned) > 1 and aligned["benchmark"].var(ddof=0) != 0:
                beta_vs_benchmark = float(
                    aligned["portfolio"].cov(aligned["benchmark"]) / aligned["benchmark"].var(ddof=0)
                )

    rolling_vol = rolling_volatility(portfolio_returns).dropna().tail(10).tolist()
    rolling_var_values = rolling_var(portfolio_returns, confidence=confidence).dropna().tail(10).tolist()
    warnings = assess_limits(historical, exposure_ticker)

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio_name,
        "strategy_style": strategy_style,
        "portfolio_objective": portfolio_objective,
        "as_of": portfolio_values.index[-1].to_pydatetime().replace(tzinfo=timezone.utc),
        "holdings": _holdings_frame(holdings).to_dict(orient="records"),
        "total_value": latest_value,
        "daily_return": daily_return,
        "cumulative_return": total_return,
        "volatility": volatility,
        "annualized_volatility": annualized,
        "historical_var_95": historical,
        "parametric_var_95": parametric,
        "expected_shortfall_95": shortfall,
        "maximum_drawdown": drawdown,
        "sharpe_ratio": sharpe,
        "beta_vs_benchmark": beta_vs_benchmark,
        "exposures_by_ticker": exposure_ticker,
        "exposures_by_asset_class": exposure_asset_class,
        "top_holdings": top_rows,
        "driver_summary": drivers,
        "rolling_volatility": rolling_vol,
        "rolling_var_95": rolling_var_values,
        "warnings": warnings,
    }
