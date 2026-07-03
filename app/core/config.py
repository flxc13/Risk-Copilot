from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


# Ensure repo .env wins over stale terminal/session variables, regardless of CWD.
_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=_REPO_ROOT / ".env", override=True)


DEFAULT_APP_NAME = "Risk Advisor Copilot"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_API_PREFIX = "/api"
DEFAULT_TICKERS: tuple[str, ...] = ("AAPL", "MSFT", "NVDA", "AMZN", "SPY", "TLT", "GLD")
DEFAULT_BENCHMARK_TICKER = "SPY"
DEFAULT_LOOKBACK_DAYS = 252
DEFAULT_RISK_CONFIDENCE = 0.95
DEFAULT_POE_BASE_URL = "https://api.poe.com/v1"
DEFAULT_POE_MODEL = "gpt-5.4"


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = DEFAULT_APP_NAME
    environment: str = DEFAULT_ENVIRONMENT
    api_prefix: str = DEFAULT_API_PREFIX
    default_tickers: tuple[str, ...] = DEFAULT_TICKERS
    benchmark_ticker: str = DEFAULT_BENCHMARK_TICKER
    demo_lookback_days: int = DEFAULT_LOOKBACK_DAYS
    risk_confidence: float = DEFAULT_RISK_CONFIDENCE
    poe_api_key: str | None = None
    poe_base_url: str = DEFAULT_POE_BASE_URL
    poe_model: str = DEFAULT_POE_MODEL


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    default_tickers = os.getenv("DEFAULT_TICKERS", ",".join(DEFAULT_TICKERS))
    normalized_tickers = tuple(
        ticker.strip().upper() for ticker in default_tickers.split(",") if ticker.strip()
    )
    poe_api_key = (os.getenv("POE_API_KEY") or "").strip() or None

    return Settings(
        app_name=os.getenv("APP_NAME", DEFAULT_APP_NAME),
        environment=os.getenv("APP_ENV", DEFAULT_ENVIRONMENT),
        api_prefix=os.getenv("API_PREFIX", DEFAULT_API_PREFIX),
        default_tickers=normalized_tickers or DEFAULT_TICKERS,
        benchmark_ticker=os.getenv("BENCHMARK_TICKER", DEFAULT_BENCHMARK_TICKER),
        demo_lookback_days=int(os.getenv("DEMO_LOOKBACK_DAYS", str(DEFAULT_LOOKBACK_DAYS))),
        risk_confidence=float(os.getenv("RISK_CONFIDENCE", str(DEFAULT_RISK_CONFIDENCE))),
        poe_api_key=poe_api_key,
        poe_base_url=os.getenv("POE_BASE_URL", DEFAULT_POE_BASE_URL),
        poe_model=os.getenv("POE_MODEL", DEFAULT_POE_MODEL),
    )
