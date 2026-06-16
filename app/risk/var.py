"""Historical simulation VaR calculations based on trades and return scenarios."""

import numpy as np
import pandas as pd

from app.models.risk_models import VaRResult


def _symbol_positions(trades_df: pd.DataFrame) -> dict[str, float]:
    if trades_df.empty:
        return {}

    direction = np.where(trades_df["side"].to_numpy() == "SELL", -1.0, 1.0)
    notionals = direction * trades_df["quantity"].to_numpy() * trades_df["price"].to_numpy()
    trades_with_notional = trades_df.copy()
    trades_with_notional["notional"] = notionals
    grouped = trades_with_notional.groupby("symbol")["notional"].sum()
    return {symbol: float(value) for symbol, value in grouped.items()}


def calculate_portfolio_var(
    trades_df: pd.DataFrame,
    historical_returns: dict[str, list[float]],
    confidence: float,
) -> VaRResult:
    positions = _symbol_positions(trades_df)
    if not positions:
        return VaRResult(confidence=confidence, var_value=0.0, method="historical")

    available_symbols = [symbol for symbol in positions if symbol in historical_returns]
    if not available_symbols:
        return VaRResult(confidence=confidence, var_value=0.0, method="historical")

    series_lengths = [len(historical_returns[symbol]) for symbol in available_symbols]
    min_len = min(series_lengths)
    if min_len == 0:
        return VaRResult(confidence=confidence, var_value=0.0, method="historical")

    pnl_series = np.zeros(min_len)
    for symbol in available_symbols:
        symbol_returns = np.array(historical_returns[symbol][:min_len], dtype=float)
        pnl_series += positions[symbol] * symbol_returns

    tail_quantile = np.quantile(pnl_series, 1.0 - confidence)
    var_value = max(0.0, float(-tail_quantile))

    return VaRResult(confidence=confidence, var_value=var_value, method="historical")
