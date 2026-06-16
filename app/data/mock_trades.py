from app.models.schemas import TradeSchema


def get_mock_trades() -> list[TradeSchema]:
    return [
        TradeSchema(trade_id="T1", symbol="AAPL", side="BUY", quantity=150, price=190),
        TradeSchema(trade_id="T2", symbol="MSFT", side="BUY", quantity=120, price=430),
        TradeSchema(trade_id="T3", symbol="TSLA", side="SELL", quantity=40, price=210),
        TradeSchema(trade_id="T4", symbol="NVDA", side="BUY", quantity=80, price=1200),
        TradeSchema(trade_id="T5", symbol="AAPL", side="SELL", quantity=20, price=192),
    ]
