from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path

import pandas as pd


DEFAULT_MARKET_DATA_CACHE_DIR = Path("data") / "cache" / "market_data"

STRESS_WINDOWS: dict[str, tuple[str, str, str]] = {
    "rates_2022": ("2022-01-03", "2022-12-30", "2022 rates/inflation shock"),
    "growth_2022": ("2021-11-01", "2022-10-31", "2021-2022 long-duration growth selloff"),
    "covid_2020": ("2020-02-19", "2020-04-30", "COVID-19 market shock"),
    "covid_2020_12m": ("2020-02-19", "2021-02-19", "COVID-19 12-month stress calibration period"),
}


@dataclass(frozen=True, slots=True)
class StressProxyRule:
    proxy_ticker: str
    return_multiplier: float
    reason: str


@dataclass(frozen=True, slots=True)
class StressMarketData:
    prices: pd.DataFrame
    window_id: str
    label: str
    proxies_used: list[dict[str, float | str]]
    coverage_warnings: list[str]
    observations: int


STRESS_PROXY_RULES: dict[str, StressProxyRule] = {
    "TQQQ": StressProxyRule("QQQ", 3.0, "Levered ETF proxy: Nasdaq 100 returns scaled by stated 3x daily leverage."),
    "SOXL": StressProxyRule("SOXX", 3.0, "Levered ETF proxy: semiconductor ETF returns scaled by stated 3x daily leverage."),
    "PSQ": StressProxyRule("QQQ", -1.0, "Inverse ETF proxy: Nasdaq 100 returns inverted when direct stress-window history is sparse."),
    "SH": StressProxyRule("SPY", -1.0, "Inverse ETF proxy: S&P 500 returns inverted when direct stress-window history is sparse."),
    "BITO": StressProxyRule("BTC-USD", 1.0, "Short-history crypto ETF proxy: bitcoin spot history used for listed futures ETF exposure."),
    "COIN": StressProxyRule("BTC-USD", 1.35, "Short-history crypto equity proxy: bitcoin returns scaled for exchange-equity beta."),
    "UVXY": StressProxyRule("VIXY", 1.5, "Volatility ETP proxy: VIX futures ETF returns scaled for levered volatility exposure."),
}


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

    try:
        raw = yf.download(
            symbols if len(symbols) > 1 else symbols[0],
            period=period,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as exc:  # pragma: no cover - depends on yfinance/network behavior
        raise MarketDataError(f"yfinance request failed: {exc}") from exc

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

    try:
        cached_frame.index = pd.to_datetime(cached_frame.index)
    except ValueError:
        cache_file.unlink(missing_ok=True)
        return None
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


def ingest_stress_prices(
    tickers: Sequence[str],
    stress_window_id: str = "rates_2022",
    cache_dir: Path | str = DEFAULT_MARKET_DATA_CACHE_DIR,
    use_cache: bool = True,
) -> tuple[pd.DataFrame, str]:
    try:
        start, end, label = STRESS_WINDOWS[stress_window_id]
    except KeyError as exc:
        available = ", ".join(sorted(STRESS_WINDOWS))
        raise MarketDataError(f"Unknown stress window '{stress_window_id}'. Available windows: {available}") from exc

    prices = ingest_historical_prices(
        tickers=tickers,
        period="max",
        start=start,
        end=end,
        cache_dir=cache_dir,
        use_cache=use_cache,
    )
    if prices.empty:
        raise MarketDataError(f"No stress market data returned for {label}")
    return prices, label


def _has_enough_observations(series: pd.Series, minimum_observations: int) -> bool:
    return int(series.dropna().shape[0]) >= minimum_observations


def _proxy_price_series(proxy_prices: pd.Series, return_multiplier: float) -> pd.Series:
    returns = proxy_prices.ffill().bfill().pct_change().fillna(0.0)
    adjusted_returns = (returns * return_multiplier).clip(lower=-0.95)
    return (1.0 + adjusted_returns).cumprod() * 100.0


def ingest_governed_stress_prices(
    tickers: Sequence[str],
    stress_window_id: str,
    cache_dir: Path | str = DEFAULT_MARKET_DATA_CACHE_DIR,
    use_cache: bool = True,
    minimum_observations: int = 40,
) -> StressMarketData:
    try:
        start, end, label = STRESS_WINDOWS[stress_window_id]
    except KeyError as exc:
        available = ", ".join(sorted(STRESS_WINDOWS))
        raise MarketDataError(f"Unknown stress window '{stress_window_id}'. Available windows: {available}") from exc

    requested_symbols = [ticker.upper() for ticker in tickers if ticker and ticker.upper() != "CASH"]
    proxy_symbols = [rule.proxy_ticker for symbol, rule in STRESS_PROXY_RULES.items() if symbol in requested_symbols]
    fetch_symbols = sorted(set(requested_symbols + proxy_symbols))
    raw_prices = ingest_historical_prices(
        tickers=fetch_symbols,
        period="max",
        start=start,
        end=end,
        cache_dir=cache_dir,
        use_cache=use_cache,
    )
    if raw_prices.empty:
        raise MarketDataError(f"No stress market data returned for {label}")

    prepared = pd.DataFrame(index=raw_prices.index)
    proxies_used: list[dict[str, float | str]] = []
    coverage_warnings: list[str] = []

    for symbol in requested_symbols:
        series = raw_prices[symbol] if symbol in raw_prices.columns else pd.Series(index=raw_prices.index, dtype=float)
        if _has_enough_observations(series, minimum_observations):
            prepared[symbol] = series.ffill().bfill()
            continue

        proxy_rule = STRESS_PROXY_RULES.get(symbol)
        if proxy_rule and proxy_rule.proxy_ticker in raw_prices.columns:
            proxy_series = raw_prices[proxy_rule.proxy_ticker]
            if _has_enough_observations(proxy_series, minimum_observations):
                prepared[symbol] = _proxy_price_series(proxy_series, proxy_rule.return_multiplier)
                proxies_used.append(
                    {
                        "ticker": symbol,
                        "proxy_ticker": proxy_rule.proxy_ticker,
                        "return_multiplier": proxy_rule.return_multiplier,
                        "reason": proxy_rule.reason,
                    }
                )
                continue

        prepared[symbol] = series.ffill().bfill()
        coverage_warnings.append(
            f"Stress history for {symbol} has fewer than {minimum_observations} observations and no usable approved proxy."
        )

    prepared = prepared.reindex(columns=requested_symbols).ffill().bfill()
    missing_symbols = [column for column in prepared.columns if prepared[column].isna().all()]
    if missing_symbols:
        raise MarketDataError(f"Stress market data unavailable for: {', '.join(missing_symbols)}")

    return StressMarketData(
        prices=prepared,
        window_id=stress_window_id,
        label=label,
        proxies_used=proxies_used,
        coverage_warnings=coverage_warnings,
        observations=int(prepared.dropna(how="all").shape[0]),
    )
