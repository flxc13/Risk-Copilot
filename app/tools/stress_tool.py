from __future__ import annotations

from pydantic import BaseModel

from app.models.schemas import StressRunResult
from app.services.stress_service import run_stress_test


class StressToolInput(BaseModel):
    portfolio_id: str = "core_long_equity"
    scenario_id: str
    use_demo_data: bool = True


def run_stress_tool(tool_input: StressToolInput) -> StressRunResult:
    return run_stress_test(
        portfolio_id=tool_input.portfolio_id,
        scenario_id=tool_input.scenario_id,
        use_demo_data=tool_input.use_demo_data,
    )