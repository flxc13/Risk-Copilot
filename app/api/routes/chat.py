from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "chat route ready"}
