"""Health-check route exposing service availability and timestamp information."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.models.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="risk-ai-copilot",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
