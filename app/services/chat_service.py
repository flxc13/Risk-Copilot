from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class CopilotAnswer:
    answer: str
    mode: str
    model: str
    citations: list[str]


def _as_float(report: Mapping[str, object], key: str) -> float:
    value = report.get(key, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _top_holding_summary(report: Mapping[str, object], limit: int = 5) -> str:
    rows = report.get("top_holdings", [])
    if not isinstance(rows, list):
        return "No top holdings available."

    summaries: list[str] = []
    for row in rows[:limit]:
        if not isinstance(row, Mapping):
            continue
        ticker = row.get("ticker", "UNKNOWN")
        weight = row.get("weight", 0.0)
        asset_class = row.get("asset_class", "Unknown")
        summaries.append(f"{ticker} {float(weight):.1%} ({asset_class})")
    return ", ".join(summaries) if summaries else "No top holdings available."


def _portfolio_context(report: Mapping[str, object]) -> str:
    exposures = report.get("exposures_by_asset_class", {})
    exposure_text = ""
    if isinstance(exposures, Mapping):
        exposure_text = ", ".join(
            f"{asset_class}: {float(weight):.1%}" for asset_class, weight in exposures.items()
        )

    warnings = report.get("warnings", [])
    warning_text = "; ".join(str(warning) for warning in warnings) if isinstance(warnings, list) else ""

    return "\n".join(
        [
            f"Portfolio: {report.get('portfolio_name', 'Unknown')}",
            f"Strategy: {report.get('strategy_style', 'Unknown')}",
            f"Objective: {report.get('portfolio_objective', 'Unknown')}",
            f"Total value: {_as_float(report, 'total_value'):,.0f}",
            f"Daily return: {_as_float(report, 'daily_return'):.2%}",
            f"Cumulative return: {_as_float(report, 'cumulative_return'):.2%}",
            f"Historical VaR 95: {_as_float(report, 'historical_var_95'):.2%}",
            f"Parametric VaR 95: {_as_float(report, 'parametric_var_95'):.2%}",
            f"Expected shortfall 95: {_as_float(report, 'expected_shortfall_95'):.2%}",
            f"Annualized volatility: {_as_float(report, 'annualized_volatility'):.2%}",
            f"Maximum drawdown: {_as_float(report, 'maximum_drawdown'):.2%}",
            f"Current drawdown: {_as_float(report, 'current_drawdown'):.2%}",
            f"Beta vs benchmark: {_as_float(report, 'beta_vs_benchmark'):.2f}",
            f"Tracking error: {_as_float(report, 'tracking_error'):.2%}",
            f"Correlation vs benchmark: {_as_float(report, 'correlation_vs_benchmark'):.2f}",
            f"Top holdings: {_top_holding_summary(report)}",
            f"Asset-class exposures: {exposure_text or 'Unavailable'}",
            f"Warnings: {warning_text or 'None'}",
        ]
    )


def _fallback_answer(question: str, report: Mapping[str, object]) -> CopilotAnswer:
    var_value = _as_float(report, "historical_var_95")
    expected_shortfall = _as_float(report, "expected_shortfall_95")
    drawdown = _as_float(report, "maximum_drawdown")
    volatility = _as_float(report, "annualized_volatility")
    beta = _as_float(report, "beta_vs_benchmark")
    top_holdings = _top_holding_summary(report, limit=3)

    answer = (
        f"I can answer in offline analyst mode until POE_API_KEY is configured. "
        f"For {report.get('portfolio_name', 'the selected portfolio')}, the current risk posture is: "
        f"historical VaR {var_value:.2%}, expected shortfall {expected_shortfall:.2%}, "
        f"annualized volatility {volatility:.2%}, maximum drawdown {drawdown:.2%}, "
        f"and beta {beta:.2f}. The largest visible exposures are {top_holdings}. "
        f"Your question was: '{question}'. A practical next review is to compare the top weights "
        f"against VaR, drawdown, and benchmark beta before changing the book."
    )
    return CopilotAnswer(
        answer=answer,
        mode="offline_fallback",
        model="local-risk-summary",
        citations=["risk_report", "top_holdings", "exposures_by_asset_class"],
    )


def answer_risk_question(question: str, report: Mapping[str, object]) -> CopilotAnswer:
    if not question.strip():
        return CopilotAnswer(
            answer="Ask a portfolio or risk question and I will summarize the current report.",
            mode="empty_question",
            model="none",
            citations=[],
        )

    settings = get_settings()
    if not settings.poe_api_key:
        return _fallback_answer(question, report)

    prompt = (
        "You are Risk Advisor Copilot, an institutional portfolio risk assistant for a small hedge fund. "
        "Be concise, specific, and grounded only in the supplied risk report. "
        "Do not invent market facts, live news, trades, or unavailable data. "
        "Structure answers with: readout, drivers, risks to inspect, and next analytical step. "
        "Avoid giving certainty-framed trading advice.\n\n"
        f"Risk report context:\n{_portfolio_context(report)}\n\n"
        f"User question: {question}"
    )

    try:
        import openai

        client = openai.OpenAI(api_key=settings.poe_api_key, base_url=settings.poe_base_url)
        response = client.responses.create(model=settings.poe_model, input=prompt)
        answer = str(response.output_text).strip()
    except Exception as exc:  # pragma: no cover - live provider path
        fallback = _fallback_answer(question, report)
        return CopilotAnswer(
            answer=f"AI provider call failed, so I used offline analyst mode. Provider error: {exc}.\n\n{fallback.answer}",
            mode="provider_error_fallback",
            model=settings.poe_model,
            citations=fallback.citations,
        )

    return CopilotAnswer(
        answer=answer,
        mode="poe_live",
        model=settings.poe_model,
        citations=["risk_report", "portfolio_catalog", "risk_metrics"],
    )
