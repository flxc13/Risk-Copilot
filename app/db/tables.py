"""Database schema creation utilities for request audit log tables."""

import sqlite3

from app.db.session import get_connection


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            request_type TEXT NOT NULL,
            input_query TEXT NOT NULL,
            tools_used TEXT NOT NULL,
            tool_outputs TEXT NOT NULL,
            retrieved_context TEXT NOT NULL,
            model_used TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            response_type TEXT NOT NULL
        )
        """
    )
    conn.commit()


def init_db() -> None:
    conn = get_connection()
    ensure_tables(conn)
