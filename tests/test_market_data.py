from __future__ import annotations

import sys
import types

import pandas as pd

from app.data.market_data import ingest_historical_prices


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