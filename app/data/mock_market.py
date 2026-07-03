from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


PROFILE_BY_TICKER: dict[str, dict[str, float]] = {
    "AAPL": {"start": 180.0, "drift": 0.0006, "vol": 0.017},
    "MSFT": {"start": 320.0, "drift": 0.0005, "vol": 0.014},
    "NVDA": {"start": 400.0, "drift": 0.0008, "vol": 0.028},
    "AMZN": {"start": 140.0, "drift": 0.00055, "vol": 0.02},
    "AVGO": {"start": 860.0, "drift": 0.00055, "vol": 0.022},
    "GOOGL": {"start": 138.0, "drift": 0.00045, "vol": 0.018},
    "META": {"start": 360.0, "drift": 0.0006, "vol": 0.023},
    "JPM": {"start": 172.0, "drift": 0.0003, "vol": 0.015},
    "XOM": {"start": 102.0, "drift": 0.00025, "vol": 0.017},
    "LLY": {"start": 560.0, "drift": 0.00055, "vol": 0.019},
    "SPY": {"start": 460.0, "drift": 0.00035, "vol": 0.01},
    "QQQ": {"start": 390.0, "drift": 0.00045, "vol": 0.014},
    "IWM": {"start": 205.0, "drift": 0.00025, "vol": 0.017},
    "XLE": {"start": 86.0, "drift": 0.0002, "vol": 0.019},
    "XLF": {"start": 38.0, "drift": 0.00025, "vol": 0.014},
    "XLV": {"start": 132.0, "drift": 0.00025, "vol": 0.01},
    "TLT": {"start": 92.0, "drift": 0.0001, "vol": 0.008},
    "LQD": {"start": 108.0, "drift": 0.00008, "vol": 0.004},
    "HYG": {"start": 76.0, "drift": 0.00012, "vol": 0.006},
    "GLD": {"start": 185.0, "drift": 0.0002, "vol": 0.009},
    "UUP": {"start": 28.0, "drift": 0.00005, "vol": 0.004},
    "PSQ": {"start": 11.0, "drift": -0.00035, "vol": 0.014},
    "SH": {"start": 13.0, "drift": -0.00025, "vol": 0.01},
    "CASH": {"start": 1.0, "drift": 0.0, "vol": 0.0},
}


def _generate_price_path(ticker: str, dates: pd.DatetimeIndex, position: int) -> pd.Series:
    normalized_ticker = ticker.upper()
    profile = PROFILE_BY_TICKER.get(
        normalized_ticker,
        {"start": 100.0, "drift": 0.0004, "vol": 0.015},
    )

    if normalized_ticker == "CASH":
        return pd.Series(1.0, index=dates, name=normalized_ticker)

    rng = np.random.default_rng(1000 + position * 97)
    shocks = rng.normal(loc=profile["drift"], scale=profile["vol"], size=len(dates))
    prices = profile["start"] * np.exp(np.cumsum(shocks))
    return pd.Series(prices, index=dates, name=normalized_ticker)


def get_demo_market_data(
    tickers: Sequence[str],
    benchmark_ticker: str = "SPY",
    periods: int = 252,
) -> tuple[pd.DataFrame, pd.Series]:
    unique_tickers = [ticker.upper() for ticker in tickers if ticker]
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=periods)

    price_frame = pd.DataFrame(
        {
            ticker: _generate_price_path(ticker, dates, position)
            for position, ticker in enumerate(unique_tickers)
        },
        index=dates,
    )
    benchmark_series = _generate_price_path(benchmark_ticker, dates, len(unique_tickers) + 1)
    benchmark_series.name = benchmark_ticker.upper()
    return price_frame, benchmark_series
