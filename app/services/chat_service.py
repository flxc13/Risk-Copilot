from __future__ import annotations

from collections.abc import Mapping


def answer_risk_question(question: str, report: Mapping[str, object]) -> str:
    if not question.strip():
        return "Ask a portfolio or risk question and I will summarize the current report."
    var_value = report.get("historical_var_95", 0.0)
    drawdown = report.get("maximum_drawdown", 0.0)
    return (
        f"The current portfolio risk view shows historical VaR at {float(var_value):.1%} "
        f"and maximum drawdown at {float(drawdown):.1%}."
    )
