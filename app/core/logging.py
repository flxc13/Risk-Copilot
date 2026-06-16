"""Request-level audit logging utilities that persist structured traces to SQLite."""

import json
import logging
from typing import Any

from app.db.session import get_connection
from app.db.tables import ensure_tables


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _json(value: Any) -> str:
    return json.dumps(value, default=str)


def log_request(
    *,
    request_id: str,
    request_type: str,
    input_query: str,
    tools_used: list[str],
    tool_outputs: dict[str, Any],
    retrieved_context: list[str],
    model_used: str,
    latency_ms: int,
    response_type: str,
) -> None:
    conn = get_connection()
    ensure_tables(conn)
    conn.execute(
        """
        INSERT INTO request_logs (
            request_id,
            request_type,
            input_query,
            tools_used,
            tool_outputs,
            retrieved_context,
            model_used,
            latency_ms,
            response_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request_id,
            request_type,
            input_query,
            _json(tools_used),
            _json(tool_outputs),
            _json(retrieved_context),
            model_used,
            latency_ms,
            response_type,
        ),
    )
    conn.commit()
