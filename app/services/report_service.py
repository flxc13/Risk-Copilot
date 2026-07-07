from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import get_settings


@dataclass(frozen=True, slots=True)
class GeneratedReport:
    title: str
    report: str
    mode: str
    model: str
    citations: list[str]


REPORT_TITLES = {
    "morning_note": "Morning Risk Report",
    "eod_wrap": "End-of-Day Risk Wrap",
    "weekly_review": "Weekly Risk Review",
    "basel_simplified_capital": "Basel-Style Risk Capital Charge Report",
}


def _as_float(report: Mapping[str, object], key: str) -> float:
    value = report.get(key, 0.0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _money(value: float) -> str:
    return f"${value:,.0f}"


def _top_holding_lines(report: Mapping[str, object], limit: int = 5) -> list[str]:
    rows = report.get("top_holdings", [])
    if not isinstance(rows, list):
        return ["- No top holdings available."]

    lines: list[str] = []
    for row in rows[:limit]:
        if not isinstance(row, Mapping):
            continue
        ticker = row.get("ticker", "UNKNOWN")
        weight = _as_float(row, "weight")
        asset_class = row.get("asset_class", "Unknown")
        market_value = _as_float(row, "market_value")
        lines.append(f"- **{ticker}**: {_pct(weight)} weight, {_money(market_value)}, {asset_class}")
    return lines or ["- No top holdings available."]


def _exposure_lines(report: Mapping[str, object]) -> list[str]:
    exposures = report.get("exposures_by_asset_class", {})
    if not isinstance(exposures, Mapping) or not exposures:
        return ["- Asset-class exposure unavailable."]
    return [f"- **{asset_class}**: {_pct(float(weight))}" for asset_class, weight in exposures.items()]


def _warning_lines(report: Mapping[str, object]) -> list[str]:
    warnings = report.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        return [f"- {warning}" for warning in warnings]
    return ["- No active VaR or concentration warnings from the configured checks."]


def _max_ticker_weight(report: Mapping[str, object]) -> float:
    exposures = report.get("exposures_by_ticker", {})
    if not isinstance(exposures, Mapping) or not exposures:
        return 0.0
    return max(float(weight) for weight in exposures.values())


def _basel_simplified_report(report: Mapping[str, object], audience: str, generated_at: str) -> GeneratedReport:
    total_value = _as_float(report, "total_value")
    var95 = _as_float(report, "historical_var_95")
    es95 = _as_float(report, "expected_shortfall_95")
    volatility = _as_float(report, "annualized_volatility")
    max_drawdown = _as_float(report, "maximum_drawdown")
    max_weight = _max_ticker_weight(report)

    stress_var = max(var95 * 1.25, es95)

    sbm_delta_charge = total_value * stress_var * 2.20
    sbm_vega_charge = total_value * max(volatility - 0.12, 0.0) * 0.35
    sbm_curvature_charge = total_value * max(max_drawdown - 0.10, 0.0) * 0.45
    sbm_total = sbm_delta_charge + sbm_vega_charge + sbm_curvature_charge

    drc_jtd_proxy = total_value * max(max_weight - 0.20, 0.0)
    drc_charge = drc_jtd_proxy * 0.08

    rrao_notional_proxy = total_value * max(volatility - 0.20, 0.0)
    rrao_charge = rrao_notional_proxy * 0.01

    sa_total = sbm_total + drc_charge + rrao_charge

    imcc_like_charge = total_value * es95 * 1.50
    pre_buffer_binding_charge = max(sa_total, imcc_like_charge)
    operational_buffer = pre_buffer_binding_charge * 0.10
    total_capital_charge = pre_buffer_binding_charge + operational_buffer
    rwa_proxy = total_capital_charge / 0.08 if total_capital_charge > 0 else 0.0

    portfolio_name = report.get("portfolio_name", "Selected portfolio")
    desk_name = report.get("strategy_style", "Unknown strategy")

    markdown = "\n".join(
        [
            f"# Basel-Style Risk Capital Charge Breakdown: {portfolio_name}",
            "",
            f"Generated: {generated_at}",
            f"Audience: {audience}",
            "Framework: Basel-style, calculation-first internal estimate",
            "",
            "> **Important:** This is an internal, simplified capital-style estimate for management use. "
            "It is **not** an FRTB-SA, FRTB-IMA, or regulatory capital submission.",
            "",
            "## Regulatory Mapping (Simplified)",
            "- Trading desk proxy: portfolio strategy bucket",
            "- Market risk module: sensitivities-based method (SBM) proxy",
            "- Default risk module: default risk charge (DRC) proxy",
            "- Residual risk module: residual risk add-on (RRAO) proxy",
            "- Internal models comparator: ES-based IMCC-style proxy",
            "",
            "## Input Risk Measures",
            f"- Desk proxy: **{desk_name}**",
            f"- Portfolio market value: **{_money(total_value)}**",
            f"- Historical VaR 95: **{_pct(var95)}**",
            f"- Expected shortfall 95: **{_pct(es95)}**",
            f"- Annualized volatility: **{_pct(volatility)}**",
            f"- Maximum drawdown: **{_pct(max_drawdown)}**",
            f"- Largest single-name weight: **{_pct(max_weight)}**",
            "",
            "## FRTB-SA Proxy: Sensitivities-Based Method (SBM)",
            f"- Stress VaR proxy = `max(VaR95 × 1.25, ES95)` = **{_pct(stress_var)}**",
            f"- Delta charge proxy = `MV × Stress VaR × 2.20` = **{_money(sbm_delta_charge)}**",
            f"- Vega charge proxy = `MV × max(Vol - 12%, 0) × 0.35` = **{_money(sbm_vega_charge)}**",
            f"- Curvature charge proxy = `MV × max(Max Drawdown - 10%, 0) × 0.45` = **{_money(sbm_curvature_charge)}**",
            f"- **SBM total = {_money(sbm_total)}**",
            "",
            "## FRTB-SA Proxy: Default Risk Charge (DRC)",
            f"- JTD proxy = `MV × max(Largest Weight - 20%, 0)` = **{_money(drc_jtd_proxy)}**",
            f"- DRC charge proxy = `JTD Proxy × 8%` = **{_money(drc_charge)}**",
            "",
            "## FRTB-SA Proxy: Residual Risk Add-On (RRAO)",
            f"- RRAO notional proxy = `MV × max(Vol - 20%, 0)` = **{_money(rrao_notional_proxy)}**",
            f"- RRAO charge proxy = `RRAO Notional Proxy × 1%` = **{_money(rrao_charge)}**",
            "",
            "## IMA Comparator Proxy",
            f"- IMCC-style charge = `MV × ES95 × 1.50` = **{_money(imcc_like_charge)}**",
            "",
            "## Capital Stack and Binding Charge",
            f"- SA total proxy = `SBM + DRC + RRAO` = **{_money(sa_total)}**",
            f"- IMA comparator proxy = **{_money(imcc_like_charge)}**",
            f"- Pre-buffer binding charge = `max(SA, IMA)` = **{_money(pre_buffer_binding_charge)}**",
            f"- Operational buffer = `10% × Binding Charge` = **{_money(operational_buffer)}**",
            f"- **Total indicative capital charge = {_money(total_capital_charge)}**",
            f"- Capital / market value = **{_pct(total_capital_charge / total_value if total_value > 0 else 0.0)}**",
            f"- RWA proxy at 8% capital ratio = **{_money(rwa_proxy)}**",
            "",
            "## Control Checks",
            *_warning_lines(report),
            "",
            "## Scope and Model Limitations",
            "- Calculation intentionally mirrors FRTB sectioning but remains a non-regulatory approximation.",
            "- No risk-factor bucketing/correlation matrices, modellability tests, NMRF charge, PLA/backtesting, or liquidity horizon scaling.",
            "- No issuer-level LGD/PD term structure, tenor decomposition, securitization treatment, or jurisdictional adjustments.",
        ]
    )
    return GeneratedReport(
        title=REPORT_TITLES["basel_simplified_capital"],
        report=markdown,
        mode="offline_sample_report",
        model="local-basel-simplified-template",
        citations=["risk_report", "exposures_by_ticker", "warnings", "risk_metrics"],
    )


def _fallback_report(report: Mapping[str, object], report_type: str, audience: str) -> GeneratedReport:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if report_type == "basel_simplified_capital":
        return _basel_simplified_report(report, audience, generated_at)

    title = REPORT_TITLES.get(report_type, REPORT_TITLES["morning_note"])
    portfolio_name = report.get("portfolio_name", "Selected portfolio")
    strategy_style = report.get("strategy_style", "Unknown strategy")
    objective = report.get("portfolio_objective", "No objective supplied.")

    markdown = "\n".join(
        [
            f"# {title}: {portfolio_name}",
            "",
            f"Generated: {generated_at}",
            f"Audience: {audience}",
            "Mode: deterministic fallback report from current sample/report data",
            "",
            "## Executive Summary",
            f"{portfolio_name} is a {strategy_style} book with total value of {_money(_as_float(report, 'total_value'))}. "
            f"The latest daily return is {_pct(_as_float(report, 'daily_return'))}, cumulative return is {_pct(_as_float(report, 'cumulative_return'))}, "
            f"and current drawdown is {_pct(_as_float(report, 'current_drawdown'))}.",
            "",
            "## Risk Snapshot",
            f"- Historical VaR 95: **{_pct(_as_float(report, 'historical_var_95'))}**",
            f"- Expected shortfall 95: **{_pct(_as_float(report, 'expected_shortfall_95'))}**",
            f"- Annualized volatility: **{_pct(_as_float(report, 'annualized_volatility'))}**",
            f"- Maximum drawdown: **{_pct(_as_float(report, 'maximum_drawdown'))}**",
            f"- Beta vs benchmark: **{_as_float(report, 'beta_vs_benchmark'):.2f}**",
            f"- Tracking error: **{_pct(_as_float(report, 'tracking_error'))}**",
            "",
            "## Top Holdings",
            *_top_holding_lines(report),
            "",
            "## Asset-Class Exposure",
            *_exposure_lines(report),
            "",
            "## Warnings and Review Items",
            *_warning_lines(report),
            "",
            "## PM Review Notes",
            f"- Objective: {objective}",
            "- Review the largest weights against VaR, expected shortfall, and benchmark beta before increasing gross exposure.",
            "- Use the Copilot chat for follow-up questions on concentration, drawdown, or benchmark divergence.",
        ]
    )
    return GeneratedReport(
        title=title,
        report=markdown,
        mode="offline_sample_report",
        model="local-report-template",
        citations=["risk_report", "top_holdings", "exposures_by_asset_class", "warnings"],
    )


def generate_report(
    report: Mapping[str, object],
    report_type: str = "morning_note",
    audience: str = "PM",
) -> GeneratedReport:
    settings = get_settings()
    fallback = _fallback_report(report, report_type, audience)
    if not settings.poe_api_key:
        return fallback

    if report_type == "basel_simplified_capital":
        output_instructions = (
            "Return markdown as a calculation breakdown, not an executive memo. "
            "Use these exact sections: Input Risk Measures, FRTB-SA Proxy: Sensitivities-Based Method (SBM), "
            "FRTB-SA Proxy: Default Risk Charge (DRC), FRTB-SA Proxy: Residual Risk Add-On (RRAO), "
            "IMA Comparator Proxy, Capital Stack and Binding Charge, Control Checks, Scope and Model Limitations. "
            "Preserve a clear disclaimer that this is non-regulatory and not an FRTB submission."
        )
    else:
        output_instructions = (
            "Return markdown with sections: Executive Summary, Risk Snapshot, Top Drivers, Warnings, PM Review Notes. "
            "Be concise and specific."
        )

    prompt = (
        "You are Risk Advisor Copilot writing an institutional portfolio risk report. "
        "Use only the supplied report context. Do not invent market news, trades, or unavailable data. "
        f"{output_instructions}\n\n"
        f"Report type: {REPORT_TITLES.get(report_type, REPORT_TITLES['morning_note'])}\n"
        f"Audience: {audience}\n"
        f"Fallback draft for grounding:\n{fallback.report}"
    )

    try:
        import openai

        client = openai.OpenAI(api_key=settings.poe_api_key, base_url=settings.poe_base_url)
        response = client.responses.create(model=settings.poe_model, input=prompt)
        text = str(response.output_text).strip()
    except Exception:
        return GeneratedReport(
            title=fallback.title,
            report=fallback.report,
            mode="provider_error_sample_report",
            model=settings.poe_model,
            citations=fallback.citations,
        )

    return GeneratedReport(
        title=fallback.title,
        report=text or fallback.report,
        mode="poe_live_report",
        model=settings.poe_model,
        citations=["risk_report", "portfolio_catalog", "risk_metrics", "top_holdings"],
    )