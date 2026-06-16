"""Service-layer workflows for /risk/compute and /risk/analyze with trace logging."""

import time
import uuid

from app.agents.orchestrator import RiskOrchestrator
from app.core.config import settings
from app.core.logging import log_request
from app.data.mock_market import get_mock_historical_returns
from app.data.mock_trades import get_mock_trades
from app.models.risk_models import RiskAnalysisResult, RiskComputationResult
from app.models.schemas import (
    LimitConfigSchema,
    RiskAnalyzeRequest,
    RiskComputeRequest,
    TradeSchema,
)


def _resolve_trades(trades: list[TradeSchema] | None) -> list[TradeSchema]:
    return trades if trades else get_mock_trades()


def _resolve_limits(limit_config: LimitConfigSchema | None) -> LimitConfigSchema:
    if limit_config:
        return limit_config
    return LimitConfigSchema(
        max_gross_exposure=settings.max_gross_exposure,
        max_var=settings.max_var,
    )


def compute_risk(request: RiskComputeRequest) -> tuple[str, RiskComputationResult]:
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    trades = _resolve_trades(request.trades)
    limits = _resolve_limits(request.limit_config)
    orchestrator = RiskOrchestrator(get_mock_historical_returns())
    result, tool_outputs = orchestrator.compute(
        trades=trades,
        confidence=request.confidence,
        limit_config=limits,
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    log_request(
        request_id=request_id,
        request_type="risk_compute",
        input_query="/risk/compute",
        tools_used=[
            "compute_portfolio_exposure",
            "calculate_var",
            "detect_limit_breach",
            "identify_risk_drivers",
        ],
        tool_outputs=tool_outputs,
        retrieved_context=[],
        model_used=settings.llm_model_name,
        latency_ms=latency_ms,
        response_type="risk_compute_result",
    )
    return request_id, result


def analyze_risk(request: RiskAnalyzeRequest) -> tuple[str, RiskAnalysisResult]:
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    trades = _resolve_trades(request.trades)
    limits = _resolve_limits(request.limit_config)
    orchestrator = RiskOrchestrator(get_mock_historical_returns())
    result, tool_outputs = orchestrator.analyze(
        trades=trades,
        confidence=request.confidence,
        limit_config=limits,
        question=request.question,
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    log_request(
        request_id=request_id,
        request_type="risk_analyze",
        input_query=request.question,
        tools_used=[
            "compute_portfolio_exposure",
            "calculate_var",
            "detect_limit_breach",
            "identify_risk_drivers",
        ],
        tool_outputs=tool_outputs,
        retrieved_context=[],
        model_used=settings.llm_model_name,
        latency_ms=latency_ms,
        response_type="risk_analysis_result",
    )
    return request_id, result
