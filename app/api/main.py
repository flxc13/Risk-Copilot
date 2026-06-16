"""FastAPI application entrypoint that wires routers and startup initialization."""

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.risk import router as risk_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.tables import init_db


logger = get_logger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health_router)
app.include_router(risk_router)
app.include_router(chat_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("Application startup complete")
