from __future__ import annotations

from app.agents.risk_interpreter import interpret_risk_report


def route_request(question: str, report: dict[str, object]) -> str:
    return interpret_risk_report(question, report)
