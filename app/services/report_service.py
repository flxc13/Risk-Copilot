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
    dashboard: dict[str, object] | None = None


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


def _list_lines(values: object, empty_message: str) -> list[str]:
    if isinstance(values, list) and values:
        return [f"- {value}" for value in values]
    return [f"- {empty_message}"]


def _stress_proxy_lines(report: Mapping[str, object]) -> list[str]:
    proxies = report.get("basel_stress_proxies_used", [])
    if not isinstance(proxies, list) or not proxies:
        return ["- No approved stress proxies were required for this portfolio/window."]

    lines: list[str] = []
    for proxy in proxies:
        if not isinstance(proxy, Mapping):
            continue
        ticker = proxy.get("ticker", "UNKNOWN")
        proxy_ticker = proxy.get("proxy_ticker", "UNKNOWN")
        multiplier = _as_float(proxy, "return_multiplier")
        reason = proxy.get("reason", "Approved stress proxy mapping.")
        lines.append(f"- **{ticker}** -> **{proxy_ticker}** at {multiplier:.2f}x daily returns: {reason}")
    return lines or ["- No approved stress proxies were required for this portfolio/window."]


def _max_ticker_weight(report: Mapping[str, object]) -> float:
    exposures = report.get("exposures_by_ticker", {})
    if not isinstance(exposures, Mapping) or not exposures:
        return 0.0
    return max(float(weight) for weight in exposures.values())


def _basel_dashboard_data(
    report: Mapping[str, object],
    audience: str,
    generated_at: str,
) -> dict[str, object]:
    total_value = _as_float(report, "total_value")
    total_charge = _as_float(report, "basel_total_capital_charge")
    observations = int(_as_float(report, "basel_backtesting_observations"))
    zone = str(report.get("basel_backtesting_zone", "insufficient"))
    zone_label = zone.upper() if zone != "insufficient" else "NOT CLASSIFIED"
    zone_reason = (
        f"{observations}/250 out-of-sample observations; traffic-light classification withheld."
        if zone == "insufficient"
        else f"{observations} out-of-sample observations support the {zone} traffic-light classification."
    )

    return {
        "portfolio_name": str(report.get("portfolio_name", "Selected portfolio")),
        "desk": str(report.get("strategy_style", "Unknown strategy")),
        "audience": audience,
        "generated_at": generated_at,
        "framework": str(report.get("basel_capital_framework", "Basel 2.5-style illustrative internal monitoring.")),
        "status": {
            "label": "INTERNAL MONITORING",
            "tone": "review",
            "traffic_light": zone,
            "traffic_light_label": zone_label,
            "traffic_light_reason": zone_reason,
        },
        "headline_metrics": [
            {"label": "Portfolio value", "value": total_value, "format": "money"},
            {"label": "Total capital", "value": total_charge, "format": "money"},
            {
                "label": "Capital intensity",
                "value": _as_float(report, "basel_capital_intensity"),
                "format": "percent",
            },
            {
                "label": "RWA equivalent",
                "value": _as_float(report, "basel_rwa_equivalent"),
                "format": "money",
            },
        ],
        "capital_stack": [
            {"label": "VaR capital leg", "value": _as_float(report, "basel_var_capital_charge"), "status": "calculated"},
            {"label": "Stressed VaR capital leg", "value": _as_float(report, "basel_stressed_var_capital_charge"), "status": "calculated"},
            {"label": "IRC", "value": _as_float(report, "basel_irc_charge"), "status": "not_implemented"},
            {"label": "CRM", "value": _as_float(report, "basel_crm_charge"), "status": "not_implemented"},
        ],
        "model_metrics": [
            {"label": "Current VaR", "value": _as_float(report, "basel_var_99_10d"), "format": "percent", "basis": "99% / 10-day"},
            {"label": "60-day average VaR", "value": _as_float(report, "basel_var_60d_avg_99_10d"), "format": "percent", "basis": f"{int(_as_float(report, 'basel_var_averaging_observations'))} estimates"},
            {"label": "Current stressed VaR", "value": _as_float(report, "basel_stressed_var_99_10d"), "format": "percent", "basis": "99% / 10-day"},
            {"label": "60-day average stressed VaR", "value": _as_float(report, "basel_stressed_var_60d_avg_99_10d"), "format": "percent", "basis": f"{int(_as_float(report, 'basel_stressed_var_averaging_observations'))} estimates"},
            {"label": "Multiplier", "value": _as_float(report, "basel_capital_multiplier"), "format": "multiple", "basis": "Provisional floor; classification withheld" if zone == "insufficient" else "Floor plus exception add-on"},
            {"label": "Exceptions", "value": int(_as_float(report, "basel_backtesting_exceptions_250d")), "format": "integer", "basis": f"{observations} forecasts"},
        ],
        "stress_governance": {
            "selected_window_id": str(report.get("basel_stress_window_id", "sample_window")),
            "selected_window": str(report.get("basel_stress_window", "Sample stress window")),
            "data_mode": str(report.get("basel_stress_data_mode", "sample_window")),
            "candidate_windows": list(report.get("basel_stress_candidate_window_ids", [])),
            "methodology": str(report.get("basel_stress_methodology", "")),
            "proxies": list(report.get("basel_stress_proxies_used", [])),
            "warnings": list(report.get("basel_svar_governance_warnings", [])),
        },
        "calculation_evidence": [
            {
                "label": "VaR leg",
                "formula": "MV x max(current VaR, m x 60-day average VaR)",
                "value": _as_float(report, "basel_var_capital_charge"),
            },
            {
                "label": "Stressed VaR leg",
                "formula": "MV x max(current sVaR, m x 60-day average sVaR)",
                "value": _as_float(report, "basel_stressed_var_capital_charge"),
            },
        ],
        "methodology": [
            str(report.get("basel_var_methodology", "")),
            str(report.get("basel_backtesting_methodology", "")),
        ],
        "limitations": list(report.get("basel_implementation_limitations", [])),
        "control_warnings": list(report.get("warnings", [])),
    }


def _basel_simplified_report(report: Mapping[str, object], audience: str, generated_at: str) -> GeneratedReport:
    total_value = _as_float(report, "total_value")
    var95 = _as_float(report, "historical_var_95")
    es95 = _as_float(report, "expected_shortfall_95")
    volatility = _as_float(report, "annualized_volatility")
    max_drawdown = _as_float(report, "maximum_drawdown")
    max_weight = _max_ticker_weight(report)

    basel_var_99_10d = _as_float(report, "basel_var_99_10d")
    basel_stressed_var_99_10d = _as_float(report, "basel_stressed_var_99_10d")
    basel_stress_window_id = str(report.get("basel_stress_window_id", "sample_window"))
    basel_stress_candidate_window_ids = report.get("basel_stress_candidate_window_ids", [])
    if isinstance(basel_stress_candidate_window_ids, list) and basel_stress_candidate_window_ids:
        basel_stress_candidate_windows = ", ".join(str(window_id) for window_id in basel_stress_candidate_window_ids)
    else:
        basel_stress_candidate_windows = basel_stress_window_id
    basel_stress_window = str(report.get("basel_stress_window", "Recent sample tail-risk window"))
    basel_stress_data_mode = str(report.get("basel_stress_data_mode", "sample_window"))
    basel_stress_methodology = str(report.get("basel_stress_methodology", "Sample-window stress selection from available returns."))
    basel_var_60d_avg_99_10d = _as_float(report, "basel_var_60d_avg_99_10d")
    basel_stressed_var_60d_avg_99_10d = _as_float(report, "basel_stressed_var_60d_avg_99_10d")
    basel_backtesting_exceptions = int(_as_float(report, "basel_backtesting_exceptions_250d"))
    basel_backtesting_observations = int(_as_float(report, "basel_backtesting_observations"))
    basel_backtesting_zone = str(report.get("basel_backtesting_zone", "green"))
    basel_capital_multiplier = _as_float(report, "basel_capital_multiplier")

    basel_var_capital_charge = _as_float(report, "basel_var_capital_charge")
    basel_stressed_var_capital_charge = _as_float(report, "basel_stressed_var_capital_charge")
    basel_irc_charge = _as_float(report, "basel_irc_charge")
    basel_crm_charge = _as_float(report, "basel_crm_charge")
    basel_total_capital_charge = _as_float(report, "basel_total_capital_charge")

    rwa_proxy = _as_float(report, "basel_rwa_equivalent") or (
        basel_total_capital_charge * 12.5 if basel_total_capital_charge > 0 else 0.0
    )

    portfolio_name = report.get("portfolio_name", "Selected portfolio")
    desk_name = report.get("strategy_style", "Unknown strategy")

    markdown = "\n".join(
        [
            f"# Legacy Basel 2.5 IMA-Style Capital Monitoring: {portfolio_name}",
            "",
            f"Generated: {generated_at}",
            f"Audience: {audience}",
            "Framework: Legacy Basel 2.5-style illustrative internal monitoring (VaR + Stressed VaR stack); not FRTB IMA",
            "",
            "> **Important:** This is an internal monitoring statement. "
            "It is **not** a legal/regulatory filing and does not represent supervisory approval status.",
            "",
            "## At a Glance",
            "| Measure | Result |",
            "|---|---:|",
            f"| Portfolio value | **{_money(total_value)}** |",
            f"| Total illustrative capital | **{_money(basel_total_capital_charge)}** |",
            f"| Capital intensity | **{_pct(basel_total_capital_charge / total_value if total_value > 0 else 0.0)}** |",
            f"| Backtesting classification | **{basel_backtesting_zone.upper() if basel_backtesting_zone != 'insufficient' else 'NOT CLASSIFIED - INSUFFICIENT OBSERVATIONS'}** |",
            "",
            "## Scope and Desk Mapping",
            f"- Reporting desk: **{desk_name}**",
            f"- Portfolio market value: **{_money(total_value)}**",
            "- Demo scope: market risk capital stack under legacy Basel 2.5-style VaR/sVaR monitoring",
            "- Modules excluded from this MVP capital stack: IRC and CRM advanced treatment (carried as explicit placeholders)",
            "",
            "## Core Risk Inputs",
            f"- Historical VaR 95 (legacy dashboard metric): **{_pct(var95)}**",
            f"- Expected shortfall 95 (legacy dashboard metric): **{_pct(es95)}**",
            f"- Annualized volatility: **{_pct(volatility)}**",
            f"- Maximum drawdown: **{_pct(max_drawdown)}**",
            f"- Largest single-name weight: **{_pct(max_weight)}**",
            "",
            "## VaR Model Outputs (99%, 10-day)",
            "- Current VaR calibration window: **recent market-data window**",
            f"- Approved candidate stress windows: **{basel_stress_candidate_windows}**",
            f"- Approved Stressed VaR window ID: **{basel_stress_window_id}**",
            f"- Stressed VaR calibration window: **{basel_stress_window}**",
            f"- Stressed VaR data mode: **{basel_stress_data_mode}**",
            f"- Stress methodology: **{basel_stress_methodology}**",
            f"- VaR(99%, 10d): **{_pct(basel_var_99_10d)}**",
            f"- Stressed VaR(99%, 10d): **{_pct(basel_stressed_var_99_10d)}**",
            f"- 60-day average VaR(99%, 10d): **{_pct(basel_var_60d_avg_99_10d)}**",
            f"- 60-day average Stressed VaR(99%, 10d): **{_pct(basel_stressed_var_60d_avg_99_10d)}**",
            "",
            "## Backtesting and Multiplier",
            f"- Backtesting window observations: **{basel_backtesting_observations}**",
            f"- Exceptions (clean-return proxy breaches): **{basel_backtesting_exceptions}**",
            f"- Traffic-light result: **{basel_backtesting_zone.upper() if basel_backtesting_zone != 'insufficient' else 'NOT CLASSIFIED'}**",
            f"- Classification note: **{'250 observations required for the standard traffic-light interpretation.' if basel_backtesting_zone == 'insufficient' else 'Observation count supports traffic-light interpretation.'}**",
            f"- Capital multiplier (m): **{basel_capital_multiplier:.2f}**",
            "",
            "## Capital Stack",
            "- Illustrative VaR leg formula: `max(current VaR, m × Avg(VaR)_60)`",
            "- Illustrative stressed VaR leg formula: `max(current sVaR, m × Avg(sVaR)_60)`",
            f"- VaR binding input: max({_pct(basel_var_99_10d)}, {_pct(basel_capital_multiplier * basel_var_60d_avg_99_10d)})",
            f"- sVaR binding input: max({_pct(basel_stressed_var_99_10d)}, {_pct(basel_capital_multiplier * basel_stressed_var_60d_avg_99_10d)})",
            f"- VaR capital leg: **{_money(basel_var_capital_charge)}**",
            f"- Stressed VaR capital leg: **{_money(basel_stressed_var_capital_charge)}**",
            f"- IRC charge (MVP placeholder): **{_money(basel_irc_charge)}**",
            f"- CRM charge (MVP placeholder): **{_money(basel_crm_charge)}**",
            f"- **Total market risk capital requirement: {_money(basel_total_capital_charge)}**",
            "",
            "## Capital Intensity and RWA Equivalent",
            f"- Capital / market value: **{_pct(basel_total_capital_charge / total_value if total_value > 0 else 0.0)}**",
            f"- RWA equivalent (capital x 12.5): **{_money(rwa_proxy)}**",
            "",
            "## Control Checks",
            *_warning_lines(report),
            "",
            "## Stress Data Governance",
            "- Stress calibration is assigned by desk/portfolio rather than selected ad hoc per request.",
            "- Current positions are revalued on the approved historical stress window.",
            "- Short-history instruments use approved proxy transformations where direct stress-window history is not available.",
            "",
            "### Approved Proxy Usage",
            *_stress_proxy_lines(report),
            "",
            "### Coverage and Governance Review Items",
            *_list_lines(
                report.get("basel_svar_governance_warnings", []),
                "No Basel sVaR governance review items raised by this run.",
            ),
            "",
            "## Methodology and Limitations",
            "- This report is legacy Basel 2.5-style internal monitoring, not a submitted Pillar 1 template or current FRTB IMA calculation.",
            "- sVaR window assignment approximates an internal-model governance workflow using approved portfolio-level windows.",
            "- IRC and CRM are represented as explicit placeholders until issuer-level migration/default and correlation-trading inputs are onboarded.",
            "- Governance workflow (independent validation, approval status, and policy attestations) is outside this API slice.",
        ]
    )
    return GeneratedReport(
        title=REPORT_TITLES["basel_simplified_capital"],
        report=markdown,
        mode="deterministic_basel_dashboard",
        model="local-basel25-monitoring-template",
        citations=[
            "risk_report",
            "basel_var_99_10d",
            "basel_stressed_var_99_10d",
            "basel_stress_window_id",
            "basel_backtesting_exceptions_250d",
            "basel_total_capital_charge",
        ],
        dashboard=_basel_dashboard_data(report, audience, generated_at),
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
    if report_type == "basel_simplified_capital" or not settings.poe_api_key:
        return fallback

    if report_type == "basel_simplified_capital":
        output_instructions = (
            "Return markdown in a Basel 2.5-style reporting format, not a narrative memo. "
            "Use these exact sections: Section 1: Reporting Scope and Desk Mapping, Section 2: Core Risk Inputs, "
            "Section 3: VaR Model Outputs (99%, 10-day), Section 4: Backtesting and Multiplier, "
            "Section 5: Capital Requirement Calculation, Section 6: Capital Intensity and RWA Proxy, "
            "Section 7: Control Checks, Section 8: Stress Data Governance, Section 9: Methodology and Limitations. "
            "Preserve a clear disclaimer that this is internal monitoring and not a regulatory filing."
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