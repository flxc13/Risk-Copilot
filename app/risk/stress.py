from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd


def run_historical_replay(
    stress_prices: pd.DataFrame,
    holdings: Sequence[Mapping[str, float | str]],
    latest_prices: Mapping[str, float],
) -> dict[str, object]:
    if stress_prices.empty:
        raise ValueError("Stress price history is empty")
    if not holdings:
        raise ValueError("Portfolio holdings are empty")

    current_values: dict[str, float] = {}
    normalized_paths: dict[str, pd.Series] = {}
    holding_metadata: dict[str, Mapping[str, float | str]] = {}

    for holding in holdings:
        ticker = str(holding["ticker"]).upper()
        current_price = 1.0 if ticker == "CASH" else float(latest_prices.get(ticker, np.nan))
        if not np.isfinite(current_price):
            raise ValueError(f"Missing current price for {ticker}")

        current_values[ticker] = float(holding["quantity"]) * current_price
        holding_metadata[ticker] = holding
        if ticker == "CASH":
            normalized_paths[ticker] = pd.Series(1.0, index=stress_prices.index)
            continue
        if ticker not in stress_prices.columns:
            raise ValueError(f"Missing stress history for {ticker}")

        series = stress_prices[ticker].ffill().bfill()
        if series.empty or series.isna().all() or float(series.iloc[0]) == 0.0:
            raise ValueError(f"Invalid stress history for {ticker}")
        normalized_paths[ticker] = series / float(series.iloc[0])

    path_frame = pd.DataFrame(normalized_paths).reindex(columns=current_values)
    current_value_series = pd.Series(current_values)
    stressed_values = path_frame.mul(current_value_series, axis=1)
    portfolio_path = stressed_values.sum(axis=1)
    current_total = float(current_value_series.sum())
    if current_total <= 0.0:
        raise ValueError("Current portfolio value must be positive")

    pnl_path = portfolio_path - current_total
    worst_date = pnl_path.idxmin()
    end_date = pnl_path.index[-1]
    worst_pnl = float(pnl_path.loc[worst_date])
    end_pnl = float(pnl_path.loc[end_date])

    position_impacts: list[dict[str, float | str]] = []
    for ticker, current_value in current_values.items():
        worst_value = float(stressed_values.loc[worst_date, ticker])
        impact = worst_value - current_value
        holding = holding_metadata[ticker]
        position_impacts.append(
            {
                "ticker": ticker,
                "asset_class": str(holding.get("asset_class", "Other")),
                "risk_bucket": str(holding.get("risk_bucket", "Unclassified")),
                "current_value": current_value,
                "stressed_value": worst_value,
                "pnl": impact,
                "return": 0.0 if current_value == 0.0 else impact / current_value,
                "loss_contribution": 0.0 if worst_pnl >= 0.0 else max(0.0, -impact) / -worst_pnl,
            }
        )

    position_impacts.sort(key=lambda row: float(row["pnl"]))
    path_records = [
        {
            "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
            "portfolio_value": float(value),
            "pnl": float(pnl_path.loc[index]),
            "return": float(value / current_total - 1.0),
        }
        for index, value in portfolio_path.items()
    ]

    attributed_pnl = sum(float(row["pnl"]) for row in position_impacts)
    if not np.isclose(attributed_pnl, worst_pnl, atol=0.01):
        raise ValueError("Position attribution does not reconcile to portfolio stress P&L")

    return {
        "current_value": current_total,
        "worst_stressed_value": current_total + worst_pnl,
        "worst_pnl": worst_pnl,
        "worst_loss": max(0.0, -worst_pnl),
        "worst_return": worst_pnl / current_total,
        "worst_date": pd.Timestamp(worst_date).strftime("%Y-%m-%d"),
        "end_stressed_value": current_total + end_pnl,
        "end_pnl": end_pnl,
        "end_return": end_pnl / current_total,
        "end_date": pd.Timestamp(end_date).strftime("%Y-%m-%d"),
        "position_impacts": position_impacts,
        "path": path_records,
        "attribution_reconciled": True,
    }