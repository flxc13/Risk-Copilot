from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.risk_service import generate_risk_report, list_available_portfolios

router = APIRouter(tags=["risk"])


@router.get("/risk/report")
def risk_report(
    use_demo_data: bool = Query(default=True),
    portfolio_id: str = Query(default="core_long_equity"),
):
    return generate_risk_report(use_demo_data=use_demo_data, portfolio_id=portfolio_id)


@router.get("/portfolios")
def portfolios() -> dict[str, list[dict[str, str]]]:
    return {"portfolios": list_available_portfolios()}
