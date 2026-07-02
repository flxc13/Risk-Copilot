from __future__ import annotations

from fastapi import APIRouter, Query

from app.data.market_data import ingest_historical_prices

router = APIRouter(tags=["market-data"])


@router.get("/market-data/history")
def historical_prices(
    tickers: list[str] = Query(default=["AAPL", "MSFT", "SPY"]),
    period: str = Query(default="1y"),
):
    price_frame = ingest_historical_prices(tickers=tickers, period=period)
    records = price_frame.reset_index()
    if not records.empty:
        date_column = records.columns[0]
        records[date_column] = records[date_column].dt.strftime("%Y-%m-%d")
        records = records.rename(columns={date_column: "date"})

    return {
        "tickers": [ticker.upper() for ticker in tickers],
        "period": period,
        "rows": len(price_frame),
        "columns": list(price_frame.columns),
        "prices": records.to_dict(orient="records"),
    }