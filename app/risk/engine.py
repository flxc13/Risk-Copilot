import pandas as pd

from app.models.risk_models import RiskComputationResult
from app.models.schemas import LimitConfigSchema, TradeSchema
from app.risk.drivers import identify_risk_drivers
from app.risk.exposure import compute_portfolio_exposure
from app.risk.limits import detect_limit_breaches
from app.risk.var import calculate_portfolio_var


def compute_risk_snapshot(
    trades: list[TradeSchema],
    historical_returns: dict[str, list[float]],
    confidence: float,
    limit_config: LimitConfigSchema,
) -> RiskComputationResult:
    trades_df = pd.DataFrame([trade.model_dump() for trade in trades])

    exposure = compute_portfolio_exposure(trades_df)
    var_result = calculate_portfolio_var(
        trades_df=trades_df,
        historical_returns=historical_returns,
        confidence=confidence,
    )
    breaches = detect_limit_breaches(
        exposure=exposure,
        var_result=var_result,
        limit_config=limit_config,
    )
    drivers = identify_risk_drivers(
        trades_df=trades_df,
        historical_returns=historical_returns,
    )

    return RiskComputationResult(
        exposure=exposure,
        var=var_result,
        breaches=breaches,
        drivers=drivers,
    )
