from app.models.risk_models import InterpretationResult, RiskComputationResult


def interpret_risk(
    computation: RiskComputationResult,
    question: str,
) -> InterpretationResult:
    breach_count = sum(1 for breach in computation.breaches if breach.breached)
    largest_driver = (
        computation.drivers.top_exposure_drivers[0].symbol
        if computation.drivers.top_exposure_drivers
        else "N/A"
    )

    explanation = (
        f"Gross exposure is {computation.exposure.gross_exposure:.2f}, net exposure is "
        f"{computation.exposure.net_exposure:.2f}, and 1-day VaR at "
        f"{computation.var.confidence:.1%} is {computation.var.var_value:.2f}. "
        f"Detected {breach_count} active limit breach(es)."
    )

    hypothesis = (
        f"Primary portfolio sensitivity appears concentrated in {largest_driver}. "
        "Recent VaR level likely reflects concentration and symbol-level return volatility."
    )

    suggestion = (
        "Consider reducing concentration in top drivers, hedge directional exposure, "
        "or tighten monitoring thresholds if breaches persist. "
        f"User focus: {question}"
    )

    return InterpretationResult(
        explanation=explanation,
        hypothesis=hypothesis,
        suggestion=suggestion,
    )
