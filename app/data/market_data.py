from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


class MarketDataError(RuntimeError):
    pass


def fetch_adjusted_close(
    tickers: Sequence[str],
    period: str = "1y",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    symbols = [ticker.upper() for ticker in tickers if ticker and ticker.upper() != "CASH"]
    if not symbols:
        return pd.DataFrame()

    try:
        import yfinance as yf
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency issue
        raise MarketDataError("yfinance is required for live market-data fetches") from exc

    raw = yf.download(
        symbols if len(symbols) > 1 else symbols[0],
        period=period,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    if raw.empty:
        raise MarketDataError("No market data returned by yfinance")

    if isinstance(raw.columns, pd.MultiIndex):
        close_frame = raw.xs("Close", axis=1, level=0)
    else:
        close_frame = raw[["Close"]].rename(columns={"Close": symbols[0]})

    close_frame.columns = [str(column).upper() for column in close_frame.columns]
    close_frame = close_frame.reindex(columns=symbols)
    return close_frame.ffill().bfill()
