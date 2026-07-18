from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.data.market_data import MarketDataError
from app.models.schemas import StressRunResult, StressScenarioSummary
from app.services.stress_service import list_stress_scenarios
from app.tools.stress_tool import StressToolInput, run_stress_tool

router = APIRouter(tags=["stress"])


class StressRunRequest(BaseModel):
    portfolio_id: str = "core_long_equity"
    scenario_id: str
    use_demo_data: bool = True


@router.get("/stress/scenarios")
def stress_scenarios(
    portfolio_id: str = Query(default="core_long_equity"),
) -> dict[str, list[StressScenarioSummary]]:
    try:
        return {"scenarios": list_stress_scenarios(portfolio_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/stress/runs")
def stress_run(request: StressRunRequest) -> StressRunResult:
    try:
        return run_stress_tool(StressToolInput(**request.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=f"Governed stress market data unavailable: {exc}") from exc