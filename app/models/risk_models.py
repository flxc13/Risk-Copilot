from pydantic import BaseModel, Field


class ExposureResult(BaseModel):
    net_exposure: float
    gross_exposure: float
    by_symbol: dict[str, float]


class VaRResult(BaseModel):
    confidence: float = Field(ge=0.5, le=0.999)
    var_value: float = Field(ge=0)
    method: str = "historical"


class LimitBreach(BaseModel):
    limit_name: str
    limit_value: float
    observed_value: float
    breached: bool
    message: str


class DriverContribution(BaseModel):
    symbol: str
    value: float
    contribution_pct: float


class DriversResult(BaseModel):
    top_exposure_drivers: list[DriverContribution]
    top_var_drivers: list[DriverContribution]


class RiskComputationResult(BaseModel):
    exposure: ExposureResult
    var: VaRResult
    breaches: list[LimitBreach]
    drivers: DriversResult


class InterpretationResult(BaseModel):
    explanation: str
    hypothesis: str
    suggestion: str


class RiskAnalysisResult(BaseModel):
    computation: RiskComputationResult
    interpretation: InterpretationResult
