from __future__ import annotations

from fastapi import APIRouter

from app.services.phase1_service import get_phase1_status

router = APIRouter(tags=["phase1"])


@router.get("/phase1/status")
def phase1_status() -> dict[str, object]:
    return get_phase1_status()