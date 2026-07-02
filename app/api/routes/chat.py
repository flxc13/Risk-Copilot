from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.chat_service import answer_risk_question
from app.services.risk_service import generate_risk_report

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


@router.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    report = generate_risk_report(use_demo_data=True)
    answer = answer_risk_question(request.question, report.model_dump())
    return {"question": request.question, "answer": answer}
