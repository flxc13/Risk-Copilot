"""Deterministic portfolio exposure aggregation by symbol and net or gross totals."""

import numpy as np
import pandas as pd

from app.models.risk_models import ExposureResult


def compute_portfolio_exposure(trades_df: pd.DataFrame) -> ExposureResult:
    if trades_df.empty:
        return ExposureResult(net_exposure=0.0, gross_exposure=0.0, by_symbol={})

    direction = np.where(trades_df["side"].to_numpy() == "SELL", -1.0, 1.0)
    signed_notional = direction * trades_df["quantity"].to_numpy() * trades_df["price"].to_numpy()

    trades_with_notional = trades_df.copy()
    trades_with_notional["signed_notional"] = signed_notional

    by_symbol_series = trades_with_notional.groupby("symbol")["signed_notional"].sum()
    by_symbol = {symbol: float(value) for symbol, value in by_symbol_series.items()}

    net_exposure = float(signed_notional.sum())
    gross_exposure = float(np.abs(signed_notional).sum())
    return ExposureResult(
        net_exposure=net_exposure,
        gross_exposure=gross_exposure,
        by_symbol=by_symbol,
    )
