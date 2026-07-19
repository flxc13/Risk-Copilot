from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.market_data import router as market_data_router
from app.api.routes.phase1 import router as phase1_router
from app.api.routes.regulatory import router as regulatory_router
from app.api.routes.regulatory_dashboard import router as regulatory_dashboard_router
from app.api.routes.reports import router as reports_router
from app.api.routes.risk import router as risk_router
from app.api.routes.stress import router as stress_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Portfolio risk analytics API for Risk Advisor Copilot.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(dashboard_router)
    app.include_router(regulatory_dashboard_router)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(market_data_router, prefix=settings.api_prefix)
    app.include_router(phase1_router, prefix=settings.api_prefix)
    app.include_router(regulatory_router, prefix=settings.api_prefix)
    app.include_router(risk_router, prefix=settings.api_prefix)
    app.include_router(stress_router, prefix=settings.api_prefix)
    app.include_router(chat_router, prefix=settings.api_prefix)
    app.include_router(reports_router, prefix=settings.api_prefix)
    return app


app = create_app()
