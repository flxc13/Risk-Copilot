from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import json

from app.core.config import get_settings
from app.services.stress_service import list_stress_scenarios, resolve_stress_scenario
from app.tools.stress_tool import StressToolInput, run_stress_tool


@dataclass(frozen=True, slots=True)
class CopilotAnswer:
    answer: str
    mode: str
    model: str
    citations: list[str]
    tool_calls: list[dict[str, object]] = field(default_factory=list)
    stress_result: dict[str, object] | None = None


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


def _stress_tool_definition(portfolio_id: str) -> dict[str, object]:
    approved = [scenario for scenario in list_stress_scenarios(portfolio_id) if scenario.approved_for_portfolio]
    scenario_ids = [scenario.scenario_id for scenario in approved]
    scenario_context = "; ".join(
        f"{scenario.scenario_id}: {scenario.label} ({scenario.start_date} to {scenario.end_date})"
        for scenario in approved
    )
    return {
        "type": "function",
        "name": "run_stress_test",
        "description": (
            "Run a governed historical stress replay on the currently selected portfolio and return "
            f"reconciled position-level P&L. Approved scenarios: {scenario_context}"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "scenario_id": {
                    "type": "string",
                    "enum": scenario_ids,
                    "description": "The approved historical scenario to execute.",
                }
            },
            "required": ["scenario_id"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def _item_value(item: object, name: str, default: object = None) -> object:
    if isinstance(item, Mapping):
        return item.get(name, default)
    return getattr(item, name, default)


def _deterministic_stress_fallback(
    question: str,
    portfolio_id: str,
    use_demo_data: bool,
    mode: str,
    model: str,
) -> CopilotAnswer | None:
    scenario_id = resolve_stress_scenario(question, portfolio_id)
    if scenario_id is None:
        return None
    result = run_stress_tool(
        StressToolInput(
            portfolio_id=portfolio_id,
            scenario_id=scenario_id,
            use_demo_data=use_demo_data,
        )
    )
    return CopilotAnswer(
        answer=result.report,
        mode=mode,
        model=model,
        citations=["stress_run", "governed_historical_prices", "position_attribution"],
        tool_calls=[{"name": "run_stress_test", "scenario_id": scenario_id}],
        stress_result=result.model_dump(mode="json", by_alias=True),
    )


def answer_risk_question_with_tools(
    question: str,
    report: Mapping[str, object],
    portfolio_id: str,
    use_demo_data: bool,
) -> CopilotAnswer:
    settings = get_settings()
    if not settings.poe_api_key:
        stress_fallback = _deterministic_stress_fallback(
            question,
            portfolio_id,
            use_demo_data,
            mode="offline_tool_fallback",
            model="historical-replay-stress-engine",
        )
        return stress_fallback or _fallback_answer(question, report)

    tool_definition = _stress_tool_definition(portfolio_id)
    prompt = (
        "You are Risk Advisor Copilot for an institutional trading desk. Use the supplied function "
        "whenever the user asks to run, execute, start, or produce a report from a stress test. "
        "Do not simulate tool output or calculate stress P&L yourself. Choose only an approved scenario. "
        "After tool execution, explain the exact returned figures with sections: Executive readout, "
        "loss drivers, governance and coverage, and limitations. Do not alter or extrapolate tool figures. "
        "If the user is not requesting execution, answer from the baseline report only.\n\n"
        f"Selected portfolio ID: {portfolio_id}\n"
        f"Baseline risk report:\n{_portfolio_context(report)}\n\n"
        f"User request: {question}"
    )

    try:
        import openai

        client = openai.OpenAI(api_key=settings.poe_api_key, base_url=settings.poe_base_url)
        first_response = client.responses.create(
            model=settings.poe_model,
            input=prompt,
            tools=[tool_definition],
            tool_choice="auto",
        )
        function_calls = [
            item
            for item in getattr(first_response, "output", [])
            if _item_value(item, "type") == "function_call"
        ]
        if not function_calls:
            return CopilotAnswer(
                answer=str(first_response.output_text).strip(),
                mode="poe_live",
                model=settings.poe_model,
                citations=["risk_report", "portfolio_catalog", "risk_metrics"],
            )

        tool_outputs: list[dict[str, object]] = []
        function_call_inputs: list[dict[str, object]] = []
        executed_calls: list[dict[str, object]] = []
        stress_result: dict[str, object] | None = None
        for function_call in function_calls:
            function_name = str(_item_value(function_call, "name", ""))
            if function_name != "run_stress_test":
                raise ValueError(f"Unsupported tool requested by model: {function_name}")
            arguments = json.loads(str(_item_value(function_call, "arguments", "{}")))
            scenario_id = str(arguments["scenario_id"])
            result = run_stress_tool(
                StressToolInput(
                    portfolio_id=portfolio_id,
                    scenario_id=scenario_id,
                    use_demo_data=use_demo_data,
                )
            )
            stress_result = result.model_dump(mode="json", by_alias=True)
            call_id = str(_item_value(function_call, "call_id", ""))
            function_call_inputs.append(
                {
                    "type": "function_call",
                    "name": function_name,
                    "arguments": json.dumps(arguments),
                    "call_id": call_id,
                }
            )
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(stress_result),
                }
            )
            executed_calls.append(
                {
                    "name": function_name,
                    "call_id": call_id,
                    "scenario_id": scenario_id,
                }
            )

        final_response = client.responses.create(
            model=settings.poe_model,
            input=[
                {"role": "user", "content": prompt},
                *function_call_inputs,
                *tool_outputs,
            ],
            tools=[tool_definition],
        )
        return CopilotAnswer(
            answer=str(final_response.output_text).strip(),
            mode="poe_tool_execution",
            model=settings.poe_model,
            citations=["stress_run", "governed_historical_prices", "position_attribution"],
            tool_calls=executed_calls,
            stress_result=stress_result,
        )
    except Exception as exc:  # pragma: no cover - provider-specific failures
        stress_fallback = _deterministic_stress_fallback(
            question,
            portfolio_id,
            use_demo_data,
            mode="provider_error_tool_fallback",
            model=settings.poe_model,
        )
        if stress_fallback is not None:
            return CopilotAnswer(
                answer=f"The LLM tool-calling request failed, so the server executed the governed tool directly. Provider error: {exc}.\n\n{stress_fallback.answer}",
                mode=stress_fallback.mode,
                model=stress_fallback.model,
                citations=stress_fallback.citations,
                tool_calls=stress_fallback.tool_calls,
                stress_result=stress_fallback.stress_result,
            )
        fallback = _fallback_answer(question, report)
        return CopilotAnswer(
            answer=f"AI provider call failed, so I used offline analyst mode. Provider error: {exc}.\n\n{fallback.answer}",
            mode="provider_error_fallback",
            model=settings.poe_model,
            citations=fallback.citations,
        )
