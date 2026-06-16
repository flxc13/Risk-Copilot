"""HTTP route for chat requests delegated to the chat service layer."""

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter(tags=["chat"])
chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
def chat_route(request: ChatRequest) -> ChatResponse:
    return chat_service.chat(request)
