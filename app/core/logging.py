from __future__ import annotations

import logging
import os


def configure_logging(level: int | str | None = None) -> None:
    resolved_level = level if level is not None else os.getenv("LOG_LEVEL", "INFO")
    if isinstance(resolved_level, str):
        resolved_level = getattr(logging, resolved_level.upper(), logging.INFO)

    logging.basicConfig(
        level=resolved_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
