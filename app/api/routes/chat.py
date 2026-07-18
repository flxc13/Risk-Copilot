from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.data.market_data import MarketDataError
from app.services.chat_service import answer_risk_question_with_tools
from app.services.risk_service import generate_risk_report

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    portfolio_id: str = "core_long_equity"
    use_demo_data: bool = True


@router.post("/chat")
def chat(request: ChatRequest) -> dict[str, object]:
    report = generate_risk_report(
        use_demo_data=request.use_demo_data,
        portfolio_id=request.portfolio_id,
    )
    try:
        answer = answer_risk_question_with_tools(
            request.question,
            report.model_dump(),
            portfolio_id=request.portfolio_id,
            use_demo_data=request.use_demo_data,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=503, detail=f"Governed stress market data unavailable: {exc}") from exc
    return {
        "question": request.question,
        "answer": answer.answer,
        "mode": answer.mode,
        "model": answer.model,
        "citations": answer.citations,
        "tool_calls": answer.tool_calls,
        "stress_result": answer.stress_result,
    }
