"""HTTP routes for risk computation and risk analysis endpoints."""

from fastapi import APIRouter

from app.models.schemas import (
    RiskAnalyzeRequest,
    RiskAnalyzeResponse,
    RiskComputeRequest,
    RiskComputeResponse,
)
from app.services.risk_service import analyze_risk, compute_risk


router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/compute", response_model=RiskComputeResponse)
def compute_risk_route(request: RiskComputeRequest) -> RiskComputeResponse:
    request_id, result = compute_risk(request)
    return RiskComputeResponse(request_id=request_id, result=result)


@router.post("/analyze", response_model=RiskAnalyzeResponse)
def analyze_risk_route(request: RiskAnalyzeRequest) -> RiskAnalyzeResponse:
    request_id, result = analyze_risk(request)
    return RiskAnalyzeResponse(request_id=request_id, result=result)
