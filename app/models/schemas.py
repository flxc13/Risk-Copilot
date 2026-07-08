from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioHolding(BaseModel):
    ticker: str
    quantity: float = Field(gt=0)
    average_cost: float = Field(ge=0)
    asset_class: str = "Other"
    sector: str = "Unclassified"
    region: str = "Global"
    position_type: str = "Long"
    liquidity_bucket: str = "Unknown"
    risk_bucket: str = "Unclassified"
    thesis: str = ""


class RiskReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    portfolio_id: str = "core_long_equity"
    portfolio_name: str = "Demo Portfolio"
    strategy_style: str = ""
    portfolio_objective: str = ""
    as_of: datetime
    holdings: list[PortfolioHolding]
    total_value: float
    daily_return: float
    cumulative_return: float
    portfolio_value_series: list[dict[str, float | str]] = Field(default_factory=list)
    portfolio_return_series: list[dict[str, float | str]] = Field(default_factory=list)
    volatility: float
    annualized_volatility: float
    historical_var_95: float
    parametric_var_95: float
    expected_shortfall_95: float
    basel_var_99_10d: float = 0.0
    basel_stressed_var_99_10d: float = 0.0
    basel_var_60d_avg_99_10d: float = 0.0
    basel_stressed_var_60d_avg_99_10d: float = 0.0
    basel_backtesting_exceptions_250d: int = 0
    basel_backtesting_observations: int = 0
    basel_backtesting_zone: str = "green"
    basel_capital_multiplier: float = 0.0
    basel_var_capital_charge: float = 0.0
    basel_stressed_var_capital_charge: float = 0.0
    basel_irc_charge: float = 0.0
    basel_crm_charge: float = 0.0
    basel_total_capital_charge: float = 0.0
    maximum_drawdown: float
    current_drawdown: float
    drawdown_series: list[dict[str, float | str]] = Field(default_factory=list)
    sharpe_ratio: float
    beta_vs_benchmark: float | None = None
    benchmark_total_return: float | None = None
    benchmark_daily_return: float | None = None
    benchmark_volatility: float | None = None
    tracking_error: float | None = None
    active_return: float | None = None
    correlation_vs_benchmark: float | None = None
    benchmark_value_series: list[dict[str, float | str]] = Field(default_factory=list)
    benchmark_return_series: list[dict[str, float | str]] = Field(default_factory=list)
    correlation_matrix: dict[str, dict[str, float]] = Field(default_factory=dict)
    exposures_by_ticker: dict[str, float] = Field(default_factory=dict)
    exposures_by_asset_class: dict[str, float] = Field(default_factory=dict)
    top_holdings: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_volatility: list[float] = Field(default_factory=list)
    rolling_var_95: list[float] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
