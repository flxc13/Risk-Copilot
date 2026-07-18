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
    basel_stress_window_id: str = "sample_window"
    basel_stress_candidate_window_ids: list[str] = Field(default_factory=list)
    basel_stress_window: str = "Recent sample tail-risk window"
    basel_stress_data_mode: str = "sample_window"
    basel_stress_methodology: str = "Sample-window stress selection from available returns."
    basel_stress_proxies_used: list[dict[str, float | str]] = Field(default_factory=list)
    basel_stress_coverage_warnings: list[str] = Field(default_factory=list)
    basel_svar_governance_warnings: list[str] = Field(default_factory=list)
    basel_var_60d_avg_99_10d: float = 0.0
    basel_stressed_var_60d_avg_99_10d: float = 0.0
    basel_var_averaging_observations: int = 0
    basel_stressed_var_averaging_observations: int = 0
    basel_backtesting_exceptions_250d: int = 0
    basel_backtesting_observations: int = 0
    basel_backtesting_zone: str = "green"
    basel_var_methodology: str = ""
    basel_backtesting_methodology: str = ""
    basel_capital_framework: str = ""
    basel_implementation_limitations: list[str] = Field(default_factory=list)
    basel_capital_multiplier: float = 0.0
    basel_var_capital_charge: float = 0.0
    basel_stressed_var_capital_charge: float = 0.0
    basel_irc_charge: float = 0.0
    basel_crm_charge: float = 0.0
    basel_total_capital_charge: float = 0.0
    basel_capital_intensity: float = 0.0
    basel_rwa_equivalent: float = 0.0
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


class StressScenarioSummary(BaseModel):
    scenario_id: str
    label: str
    start_date: str
    end_date: str
    approved_for_portfolio: bool


class StressPositionImpact(BaseModel):
    ticker: str
    asset_class: str
    risk_bucket: str
    current_value: float
    stressed_value: float
    pnl: float
    return_: float = Field(alias="return")
    loss_contribution: float


class StressPathPoint(BaseModel):
    date: str
    portfolio_value: float
    pnl: float
    return_: float = Field(alias="return")


class StressRunResult(BaseModel):
    run_id: str
    generated_at: datetime
    portfolio_id: str
    portfolio_name: str
    scenario_id: str
    scenario_label: str
    scenario_start_date: str
    scenario_end_date: str
    data_mode: str
    methodology: str
    current_value: float
    worst_stressed_value: float
    worst_pnl: float
    worst_loss: float
    worst_return: float
    worst_date: str
    end_stressed_value: float
    end_pnl: float
    end_return: float
    end_date: str
    position_impacts: list[StressPositionImpact]
    path: list[StressPathPoint]
    proxies_used: list[dict[str, float | str]] = Field(default_factory=list)
    coverage_warnings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    attribution_reconciled: bool
    report: str
