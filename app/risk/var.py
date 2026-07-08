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


def basel_historical_var(returns: pd.Series, confidence: float = 0.99, horizon_days: int = 10) -> float:
    if returns.empty:
        return 0.0
    one_day_var = historical_var(returns, confidence=confidence)
    return float(one_day_var * np.sqrt(max(horizon_days, 1)))


def _stress_window_slice(returns: pd.Series, window: int = 125) -> pd.Series:
    if returns.empty:
        return returns
    if window <= 1 or len(returns) <= window:
        return returns

    rolling_mean = returns.rolling(window=window).mean().dropna()
    if rolling_mean.empty:
        return returns

    stress_end = rolling_mean.idxmin()
    end_pos = returns.index.get_loc(stress_end)
    if isinstance(end_pos, slice):
        end_pos = end_pos.stop - 1
    if isinstance(end_pos, np.ndarray):
        end_pos = int(end_pos[-1])

    start_pos = max(int(end_pos) - window + 1, 0)
    return returns.iloc[start_pos : int(end_pos) + 1]


def basel_stressed_historical_var(
    returns: pd.Series,
    confidence: float = 0.99,
    horizon_days: int = 10,
    stress_window: int = 125,
) -> float:
    if returns.empty:
        return 0.0
    stressed_slice = _stress_window_slice(returns, window=stress_window)
    return basel_historical_var(stressed_slice, confidence=confidence, horizon_days=horizon_days)


def basel_backtesting_exceptions(
    returns: pd.Series,
    confidence: float = 0.99,
    backtesting_window: int = 250,
) -> tuple[int, int]:
    if returns.empty:
        return 0, 0

    sample = returns.tail(max(backtesting_window, 1))
    var_99_1d = historical_var(sample, confidence=confidence)
    exceptions = int((sample < -var_99_1d).sum())
    return exceptions, int(len(sample))


def basel_traffic_light_zone(exceptions: int) -> str:
    if exceptions <= 4:
        return "green"
    if exceptions <= 9:
        return "yellow"
    return "red"


def basel_multiplier(exceptions: int, floor: float = 3.0) -> float:
    add_on_map = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.40,
        6: 0.50,
        7: 0.65,
        8: 0.75,
        9: 0.85,
    }
    add_on = add_on_map.get(exceptions, 1.0)
    return float(max(floor, floor + add_on))
