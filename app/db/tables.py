from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class RiskSnapshot:
    created_at: datetime
    payload: dict[str, object] = field(default_factory=dict)
