from pydantic import BaseModel, Field

from app.models.risk_models import RiskAnalysisResult, RiskComputationResult


class TradeSchema(BaseModel):
    trade_id: str
    symbol: str
    side: str = Field(pattern="^(BUY|SELL)$")
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)


class LimitConfigSchema(BaseModel):
    max_gross_exposure: float = Field(gt=0)
    max_var: float = Field(gt=0)


class RiskComputeRequest(BaseModel):
    trades: list[TradeSchema] | None = None
    confidence: float = Field(default=0.95, ge=0.5, le=0.999)
    limit_config: LimitConfigSchema | None = None


class RiskComputeResponse(BaseModel):
    request_id: str
    result: RiskComputationResult


class RiskAnalyzeRequest(BaseModel):
    trades: list[TradeSchema] | None = None
    confidence: float = Field(default=0.95, ge=0.5, le=0.999)
    limit_config: LimitConfigSchema | None = None
    question: str = "Summarize current risk posture"


class RiskAnalyzeResponse(BaseModel):
    request_id: str
    result: RiskAnalysisResult


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    trades: list[TradeSchema] | None = None


class ChatResponse(BaseModel):
    request_id: str
    response_type: str
    message: str
    analysis: RiskAnalysisResult | None = None
    citations: list[str] = []


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
