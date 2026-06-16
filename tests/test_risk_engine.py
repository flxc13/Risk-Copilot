"""Unit test covering deterministic risk components on representative mock inputs."""

import pandas as pd

from app.data.mock_market import get_mock_historical_returns
from app.data.mock_trades import get_mock_trades
from app.models.schemas import LimitConfigSchema
from app.risk.drivers import identify_risk_drivers
from app.risk.exposure import compute_portfolio_exposure
from app.risk.limits import detect_limit_breaches
from app.risk.var import calculate_portfolio_var


def test_risk_components() -> None:
    trades = get_mock_trades()
    trades_df = pd.DataFrame([trade.model_dump() for trade in trades])
    returns = get_mock_historical_returns()

    exposure = compute_portfolio_exposure(trades_df)
    var_result = calculate_portfolio_var(trades_df, returns, confidence=0.95)
    breaches = detect_limit_breaches(
        exposure,
        var_result,
        LimitConfigSchema(max_gross_exposure=5_000_000, max_var=200_000),
    )
    drivers = identify_risk_drivers(trades_df, returns)

    assert exposure.gross_exposure > 0
    assert var_result.var_value >= 0
    assert len(breaches) == 2
    assert len(drivers.top_exposure_drivers) >= 1
