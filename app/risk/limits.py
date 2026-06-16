from app.models.risk_models import ExposureResult, LimitBreach, VaRResult
from app.models.schemas import LimitConfigSchema


def detect_limit_breaches(
    exposure: ExposureResult,
    var_result: VaRResult,
    limit_config: LimitConfigSchema,
) -> list[LimitBreach]:
    gross_breached = exposure.gross_exposure > limit_config.max_gross_exposure
    var_breached = var_result.var_value > limit_config.max_var

    return [
        LimitBreach(
            limit_name="max_gross_exposure",
            limit_value=limit_config.max_gross_exposure,
            observed_value=exposure.gross_exposure,
            breached=gross_breached,
            message=(
                "Gross exposure above limit"
                if gross_breached
                else "Gross exposure within limit"
            ),
        ),
        LimitBreach(
            limit_name="max_var",
            limit_value=limit_config.max_var,
            observed_value=var_result.var_value,
            breached=var_breached,
            message="VaR above limit" if var_breached else "VaR within limit",
        ),
    ]
