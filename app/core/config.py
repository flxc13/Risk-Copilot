"""Application configuration definitions loaded from environment settings."""

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Risk AI Copilot"
    sqlite_db_path: str = "risk_logs.db"
    var_confidence: float = Field(default=0.95, ge=0.5, le=0.999)
    max_gross_exposure: float = 2_000_000.0
    max_var: float = 150_000.0
    chroma_path: str = ".chroma"
    llm_model_name: str = "mock-llm-v1"


def _to_float(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Risk AI Copilot"),
        sqlite_db_path=os.getenv("SQLITE_DB_PATH", "risk_logs.db"),
        var_confidence=_to_float(os.getenv("VAR_CONFIDENCE", "0.95"), 0.95),
        max_gross_exposure=_to_float(
            os.getenv("MAX_GROSS_EXPOSURE", "2000000"), 2_000_000.0
        ),
        max_var=_to_float(os.getenv("MAX_VAR", "150000"), 150_000.0),
        chroma_path=os.getenv("CHROMA_PATH", ".chroma"),
        llm_model_name=os.getenv("LLM_MODEL_NAME", "mock-llm-v1"),
    )


settings = get_settings()
