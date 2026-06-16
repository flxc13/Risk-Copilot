import pandas as pd
from pydantic import BaseModel, Field

from app.models.risk_models import DriversResult
from app.models.schemas import TradeSchema
from app.risk.drivers import identify_risk_drivers


class DriversToolInput(BaseModel):
    trades: list[TradeSchema]
    historical_returns: dict[str, list[float]]
    top_n: int = Field(default=3, ge=1, le=10)


class DriversToolOutput(BaseModel):
    drivers: DriversResult


def run_drivers_tool(payload: DriversToolInput) -> DriversToolOutput:
    trades_df = pd.DataFrame([trade.model_dump() for trade in payload.trades])
    drivers = identify_risk_drivers(
        trades_df=trades_df,
        historical_returns=payload.historical_returns,
        top_n=payload.top_n,
    )
    return DriversToolOutput(drivers=drivers)
