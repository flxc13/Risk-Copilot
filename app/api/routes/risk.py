from fastapi import APIRouter

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/summary")
def summary() -> dict[str, str]:
    return {"message": "risk summary placeholder"}
