from __future__ import annotations


def interpret_risk_report(question: str, report: dict[str, object]) -> str:
    var_value = float(report.get("historical_var_95", 0.0))
    drawdown = float(report.get("maximum_drawdown", 0.0))
    if not question.strip():
        return "Ask about VaR, drawdown, volatility, or exposure and I will summarize the current report."
    return (
        f"The portfolio currently shows historical VaR at {var_value:.1%} and "
        f"maximum drawdown at {drawdown:.1%}."
    )
