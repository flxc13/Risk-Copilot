from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    url: str = "sqlite:///./risk_advisor.db"


DEFAULT_DATABASE_SETTINGS = DatabaseSettings()
