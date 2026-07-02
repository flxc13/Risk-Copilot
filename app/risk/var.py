from __future__ import annotations

import numpy as np
import pandas as pd
from statistics import NormalDist


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    if returns.empty:
        return 0.0
    return float(max(0.0, -returns.quantile(1 - confidence)))


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    if returns.empty:
        return 0.0
    mean_return = float(returns.mean())
    std_dev = float(returns.std(ddof=0))
    tail_return = mean_return + NormalDist().inv_cdf(1 - confidence) * std_dev
    return float(max(0.0, -tail_return))


def expected_shortfall(returns: pd.Series, confidence: float = 0.95) -> float:
    if returns.empty:
        return 0.0
    threshold = returns.quantile(1 - confidence)
    tail_losses = returns[returns <= threshold]
    if tail_losses.empty:
        return 0.0
    return float(max(0.0, -tail_losses.mean()))


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    if returns.empty:
        return 0.0
    return float(returns.std(ddof=0) * np.sqrt(periods_per_year))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    if returns.empty:
        return 0.0
    excess_return = returns.mean() - risk_free_rate / periods_per_year
    volatility = returns.std(ddof=0)
    if volatility == 0:
        return 0.0
    return float((excess_return / volatility) * np.sqrt(periods_per_year))


def rolling_volatility(returns: pd.Series, window: int = 21, periods_per_year: int = 252) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)
    return returns.rolling(window=window).std(ddof=0) * np.sqrt(periods_per_year)


def rolling_var(returns: pd.Series, window: int = 21, confidence: float = 0.95) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)

    def _window_var(values: pd.Series) -> float:
        return historical_var(values, confidence=confidence)

    return returns.rolling(window=window).apply(_window_var, raw=False)
