"""Typed tool wrapper for deterministic portfolio exposure computation."""

import pandas as pd
from pydantic import BaseModel

from app.models.risk_models import ExposureResult
from app.models.schemas import TradeSchema
from app.risk.exposure import compute_portfolio_exposure


class ExposureToolInput(BaseModel):
    trades: list[TradeSchema]


class ExposureToolOutput(BaseModel):
    exposure: ExposureResult


def run_exposure_tool(payload: ExposureToolInput) -> ExposureToolOutput:
    trades_df = pd.DataFrame([trade.model_dump() for trade in payload.trades])
    return ExposureToolOutput(exposure=compute_portfolio_exposure(trades_df))
