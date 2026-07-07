from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.report_service import generate_report
from app.services.risk_service import generate_risk_report

router = APIRouter(tags=["reports"])


class ReportGenerateRequest(BaseModel):
    portfolio_id: str = "core_long_equity"
    use_demo_data: bool = True
    report_type: str = "morning_note"
    audience: str = "PM"


@router.post("/reports/generate")
def generate_risk_report_markdown(request: ReportGenerateRequest) -> dict[str, str | list[str]]:
    risk_report = generate_risk_report(
        use_demo_data=request.use_demo_data,
        portfolio_id=request.portfolio_id,
    )
    generated = generate_report(
        risk_report.model_dump(),
        report_type=request.report_type,
        audience=request.audience,
    )
    return {
        "portfolio_id": risk_report.portfolio_id,
        "title": generated.title,
        "report": generated.report,
        "mode": generated.mode,
        "model": generated.model,
        "citations": generated.citations,
    }