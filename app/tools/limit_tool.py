"""Typed tool wrapper for deterministic risk limit breach detection."""

from pydantic import BaseModel

from app.models.risk_models import ExposureResult, LimitBreach, VaRResult
from app.models.schemas import LimitConfigSchema
from app.risk.limits import detect_limit_breaches


class LimitToolInput(BaseModel):
    exposure: ExposureResult
    var_result: VaRResult
    limit_config: LimitConfigSchema


class LimitToolOutput(BaseModel):
    breaches: list[LimitBreach]


def run_limit_tool(payload: LimitToolInput) -> LimitToolOutput:
    breaches = detect_limit_breaches(
        exposure=payload.exposure,
        var_result=payload.var_result,
        limit_config=payload.limit_config,
    )
    return LimitToolOutput(breaches=breaches)
