from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha1
from pathlib import Path

import pandas as pd


DEFAULT_MARKET_DATA_CACHE_DIR = Path("data") / "cache" / "market_data"


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


def _cache_key(tickers: Sequence[str], period: str, start: str | None, end: str | None) -> str:
    payload = "|".join(
        [
            ",".join(sorted(ticker.upper() for ticker in tickers if ticker)),
            period,
            start or "",
            end or "",
        ]
    )
    return sha1(payload.encode("utf-8")).hexdigest()


def _cache_path(
    tickers: Sequence[str],
    period: str,
    start: str | None,
    end: str | None,
    cache_dir: Path,
) -> Path:
    return cache_dir / f"{_cache_key(tickers, period, start, end)}.csv"


def _read_cached_prices(cache_file: Path) -> pd.DataFrame | None:
    if not cache_file.exists():
        return None

    cached_frame = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    if cached_frame.empty:
        return None

    cached_frame.index = pd.to_datetime(cached_frame.index)
    cached_frame.columns = [str(column).upper() for column in cached_frame.columns]
    return cached_frame


def _write_cached_prices(cache_file: Path, price_frame: pd.DataFrame) -> None:
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    price_frame.to_csv(cache_file)


def ingest_historical_prices(
    tickers: Sequence[str],
    period: str = "1y",
    start: str | None = None,
    end: str | None = None,
    cache_dir: Path | str = DEFAULT_MARKET_DATA_CACHE_DIR,
    use_cache: bool = True,
) -> pd.DataFrame:
    symbols = [ticker.upper() for ticker in tickers if ticker and ticker.upper() != "CASH"]
    if not symbols:
        return pd.DataFrame()

    resolved_cache_dir = Path(cache_dir)
    cache_file = _cache_path(symbols, period, start, end, resolved_cache_dir)

    if use_cache:
        cached_frame = _read_cached_prices(cache_file)
        if cached_frame is not None:
            return cached_frame.reindex(columns=symbols).ffill().bfill()

    price_frame = fetch_adjusted_close(symbols, period=period, start=start, end=end)
    _write_cached_prices(cache_file, price_frame)
    return price_frame
