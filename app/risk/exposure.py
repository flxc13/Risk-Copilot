from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd


def _normalized_values(holdings: Sequence[Mapping[str, float | str]], latest_prices: Mapping[str, float]) -> dict[str, float]:
    values: dict[str, float] = {}
    for holding in holdings:
        ticker = str(holding["ticker"]).upper()
        quantity = float(holding["quantity"])
        latest_price = 1.0 if ticker == "CASH" else float(latest_prices.get(ticker, 0.0))
        values[ticker] = quantity * latest_price
    return values


def exposure_by_ticker(
    holdings: Sequence[Mapping[str, float | str]],
    latest_prices: Mapping[str, float],
) -> dict[str, float]:
    values = _normalized_values(holdings, latest_prices)
    total_value = sum(values.values())
    if total_value == 0:
        return {ticker: 0.0 for ticker in values}
    return {ticker: value / total_value for ticker, value in values.items()}


def exposure_by_asset_class(
    holdings: Sequence[Mapping[str, float | str]],
    latest_prices: Mapping[str, float],
) -> dict[str, float]:
    values = _normalized_values(holdings, latest_prices)
    total_value = sum(values.values())
    grouped: dict[str, float] = {}
    for holding in holdings:
        asset_class = str(holding.get("asset_class", "Other"))
        ticker = str(holding["ticker"]).upper()
        grouped[asset_class] = grouped.get(asset_class, 0.0) + values.get(ticker, 0.0)

    if total_value == 0:
        return {asset_class: 0.0 for asset_class in grouped}
    return {asset_class: value / total_value for asset_class, value in grouped.items()}


def top_holdings(
    holdings: Sequence[Mapping[str, float | str]],
    latest_prices: Mapping[str, float],
    limit: int = 5,
) -> list[dict[str, float | str]]:
    values = _normalized_values(holdings, latest_prices)
    total_value = sum(values.values())
    rows: list[dict[str, float | str]] = []
    for holding in holdings:
        ticker = str(holding["ticker"]).upper()
        value = values.get(ticker, 0.0)
        rows.append(
            {
                "ticker": ticker,
                "market_value": value,
                "weight": 0.0 if total_value == 0 else value / total_value,
                "asset_class": str(holding.get("asset_class", "Other")),
            }
        )
    rows.sort(key=lambda row: float(row["market_value"]), reverse=True)
    return rows[:limit]
