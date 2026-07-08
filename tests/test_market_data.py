from __future__ import annotations

import sys
import types

import pandas as pd

from app.data.market_data import ingest_governed_stress_prices, ingest_historical_prices, ingest_stress_prices


def test_ingest_historical_prices_uses_cache(tmp_path, monkeypatch) -> None:
    calls: list[object] = []

    def fake_download(*args, **kwargs):
        calls.append((args, kwargs))
        return pd.DataFrame(
            data=[[100.0, 200.0], [101.0, 202.0]],
            index=pd.to_datetime(["2026-01-01", "2026-01-02"]),
            columns=pd.MultiIndex.from_tuples([("Close", "AAPL"), ("Close", "MSFT")]),
        )

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=fake_download))

    first_frame = ingest_historical_prices(["AAPL", "MSFT"], cache_dir=tmp_path)
    second_frame = ingest_historical_prices(["AAPL", "MSFT"], cache_dir=tmp_path)

    assert list(first_frame.columns) == ["AAPL", "MSFT"]
    assert first_frame.equals(second_frame)
    assert len(calls) == 1


def test_ingest_stress_prices_uses_named_real_market_window(tmp_path, monkeypatch) -> None:
    calls: list[object] = []

    def fake_download(*args, **kwargs):
        calls.append((args, kwargs))
        return pd.DataFrame(
            data=[[100.0], [90.0]],
            index=pd.to_datetime(["2022-01-03", "2022-01-04"]),
            columns=pd.MultiIndex.from_tuples([("Close", "QQQ")]),
        )

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=fake_download))

    stress_frame, label = ingest_stress_prices(["QQQ"], stress_window_id="rates_2022", cache_dir=tmp_path)

    assert label == "2022 rates/inflation shock"
    assert list(stress_frame.columns) == ["QQQ"]
    assert calls[0][1]["start"] == "2022-01-03"
    assert calls[0][1]["end"] == "2022-12-30"


def test_ingest_governed_stress_prices_applies_approved_proxy(tmp_path, monkeypatch) -> None:
    def fake_download(*args, **kwargs):
        dates = pd.date_range("2020-02-19", periods=45, freq="B")
        return pd.DataFrame(
            data=[[100.0 + index] for index, _ in enumerate(dates)],
            index=dates,
            columns=pd.MultiIndex.from_tuples([("Close", "BTC-USD")]),
        )

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=fake_download))

    stress_data = ingest_governed_stress_prices(["BITO"], stress_window_id="covid_2020", cache_dir=tmp_path)

    assert list(stress_data.prices.columns) == ["BITO"]
    assert stress_data.window_id == "covid_2020"
    assert stress_data.proxies_used[0]["ticker"] == "BITO"
    assert stress_data.proxies_used[0]["proxy_ticker"] == "BTC-USD"
    assert stress_data.coverage_warnings == []