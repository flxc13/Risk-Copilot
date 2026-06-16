"""Coordinates deterministic tool calls and packages computation plus interpretation outputs."""

from app.agents.risk_interpreter import interpret_risk
from app.models.risk_models import RiskAnalysisResult, RiskComputationResult
from app.models.schemas import LimitConfigSchema, TradeSchema
from app.tools.drivers_tool import DriversToolInput, run_drivers_tool
from app.tools.exposure_tool import ExposureToolInput, run_exposure_tool
from app.tools.limit_tool import LimitToolInput, run_limit_tool
from app.tools.var_tool import VaRToolInput, run_var_tool


class RiskOrchestrator:
    def __init__(self, historical_returns: dict[str, list[float]]) -> None:
        self.historical_returns = historical_returns

    def compute(
        self,
        trades: list[TradeSchema],
        confidence: float,
        limit_config: LimitConfigSchema,
    ) -> tuple[RiskComputationResult, dict[str, dict]]:
        exposure_out = run_exposure_tool(ExposureToolInput(trades=trades))
        var_out = run_var_tool(
            VaRToolInput(
                trades=trades,
                historical_returns=self.historical_returns,
                confidence=confidence,
            )
        )
        limit_out = run_limit_tool(
            LimitToolInput(
                exposure=exposure_out.exposure,
                var_result=var_out.var_result,
                limit_config=limit_config,
            )
        )
        drivers_out = run_drivers_tool(
            DriversToolInput(
                trades=trades,
                historical_returns=self.historical_returns,
                top_n=3,
            )
        )

        result = RiskComputationResult(
            exposure=exposure_out.exposure,
            var=var_out.var_result,
            breaches=limit_out.breaches,
            drivers=drivers_out.drivers,
        )
        tool_outputs = {
            "compute_portfolio_exposure": exposure_out.model_dump(),
            "calculate_var": var_out.model_dump(),
            "detect_limit_breach": limit_out.model_dump(),
            "identify_risk_drivers": drivers_out.model_dump(),
        }
        return result, tool_outputs

    def analyze(
        self,
        trades: list[TradeSchema],
        confidence: float,
        limit_config: LimitConfigSchema,
        question: str,
    ) -> tuple[RiskAnalysisResult, dict[str, dict]]:
        computation, tool_outputs = self.compute(
            trades=trades,
            confidence=confidence,
            limit_config=limit_config,
        )
        interpretation = interpret_risk(computation, question=question)
        return RiskAnalysisResult(computation=computation, interpretation=interpretation), tool_outputs
