from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Query

from app.models.regulatory import NewsletterIssue, RegulatoryRefreshResult, RegulatoryUpdate
from app.services.regulatory_service import RegulatoryService


router = APIRouter(tags=["regulatory-intelligence"])


@lru_cache(maxsize=1)
def get_regulatory_service() -> RegulatoryService:
    return RegulatoryService()


@router.get("/regulatory/updates", response_model=list[RegulatoryUpdate])
def regulatory_updates(
    jurisdiction: str | None = None,
    topic: str | None = None,
    limit: int = Query(default=100, ge=1, le=250),
) -> list[RegulatoryUpdate]:
    return get_regulatory_service().list_updates(
        jurisdiction=jurisdiction,
        topic=topic,
        limit=limit,
    )


@router.post("/regulatory/refresh", response_model=RegulatoryRefreshResult)
def refresh_regulatory_updates() -> RegulatoryRefreshResult:
    return get_regulatory_service().refresh()


@router.get("/regulatory/newsletters", response_model=list[NewsletterIssue])
def regulatory_newsletters(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[NewsletterIssue]:
    return get_regulatory_service().list_newsletters(limit=limit)


@router.post("/regulatory/newsletters/generate", response_model=NewsletterIssue)
def generate_regulatory_newsletter() -> NewsletterIssue:
    return get_regulatory_service().generate_newsletter()


@router.get("/regulatory/schedule")
def regulatory_schedule() -> dict[str, object]:
    return {
        "enabled": False,
        "frequency": "weekly",
        "status": "placeholder",
        "message": "Scheduled generation is reserved for a later deployment slice; on-demand generation is active.",
    }