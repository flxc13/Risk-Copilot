"""Deterministic risk driver attribution logic for exposure and VaR proxy contributions."""

import numpy as np
import pandas as pd

from app.models.risk_models import DriverContribution, DriversResult


def identify_risk_drivers(
    trades_df: pd.DataFrame,
    historical_returns: dict[str, list[float]],
    top_n: int = 3,
) -> DriversResult:
    if trades_df.empty:
        return DriversResult(top_exposure_drivers=[], top_var_drivers=[])

    direction = np.where(trades_df["side"].to_numpy() == "SELL", -1.0, 1.0)
    notionals = direction * trades_df["quantity"].to_numpy() * trades_df["price"].to_numpy()
    trades_with_notional = trades_df.copy()
    trades_with_notional["notional"] = notionals

    exposure_by_symbol = (
        trades_with_notional.groupby("symbol")["notional"].sum().sort_values(key=np.abs, ascending=False)
    )
    total_abs_exposure = float(np.abs(exposure_by_symbol).sum()) or 1.0

    exposure_drivers: list[DriverContribution] = []
    for symbol, value in exposure_by_symbol.head(top_n).items():
        contribution = float(abs(value) / total_abs_exposure)
        exposure_drivers.append(
            DriverContribution(symbol=symbol, value=float(value), contribution_pct=contribution)
        )

    var_proxy = {}
    for symbol, value in exposure_by_symbol.items():
        symbol_returns = historical_returns.get(symbol, [])
        std = float(np.std(symbol_returns)) if symbol_returns else 0.0
        var_proxy[symbol] = abs(float(value)) * std

    sorted_var_proxy = sorted(var_proxy.items(), key=lambda item: item[1], reverse=True)
    total_var_proxy = sum(v for _, v in sorted_var_proxy) or 1.0
    var_drivers = [
        DriverContribution(
            symbol=symbol,
            value=float(score),
            contribution_pct=float(score / total_var_proxy),
        )
        for symbol, score in sorted_var_proxy[:top_n]
    ]

    return DriversResult(
        top_exposure_drivers=exposure_drivers,
        top_var_drivers=var_drivers,
    )
