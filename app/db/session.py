"""SQLite connection factory used by logging and table management helpers."""

import sqlite3

from app.core.config import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.sqlite_db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
