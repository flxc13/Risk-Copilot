"""Typed tool wrapper for deterministic historical VaR computation."""

import pandas as pd
from pydantic import BaseModel, Field

from app.models.risk_models import VaRResult
from app.models.schemas import TradeSchema
from app.risk.var import calculate_portfolio_var


class VaRToolInput(BaseModel):
    trades: list[TradeSchema]
    historical_returns: dict[str, list[float]]
    confidence: float = Field(ge=0.5, le=0.999)


class VaRToolOutput(BaseModel):
    var_result: VaRResult


def run_var_tool(payload: VaRToolInput) -> VaRToolOutput:
    trades_df = pd.DataFrame([trade.model_dump() for trade in payload.trades])
    var_result = calculate_portfolio_var(
        trades_df=trades_df,
        historical_returns=payload.historical_returns,
        confidence=payload.confidence,
    )
    return VaRToolOutput(var_result=var_result)
