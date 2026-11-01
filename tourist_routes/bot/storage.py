"""Обране користувачів Telegram у SQLite."""
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


class FavoritesStorage:
    def __init__(self, db_file):
        self.db_file = str(db_file)
        if self.db_file != ":memory:":
            Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS favorites ("
                " user_id INTEGER NOT NULL, route_id INTEGER NOT NULL, added_at TEXT NOT NULL,"
                " PRIMARY KEY (user_id, route_id))"
            )

    def _connect(self):
        return closing_connection(self.db_file)

    def add(self, user_id: int, route_id: int) -> bool:
        """Повертає True, якщо маршрут додано, False — якщо він уже був в обраному."""
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO favorites (user_id, route_id, added_at) VALUES (?, ?, ?)",
                (user_id, route_id, datetime.now(timezone.utc).isoformat()),
            )
            return cursor.rowcount > 0

    def remove(self, user_id: int, route_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM favorites WHERE user_id = ? AND route_id = ?", (user_id, route_id)
            )
            return cursor.rowcount > 0

    def is_favorite(self, user_id: int, route_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM favorites WHERE user_id = ? AND route_id = ?", (user_id, route_id)
            ).fetchone()
            return row is not None

    def list_ids(self, user_id: int) -> list:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT route_id FROM favorites WHERE user_id = ? ORDER BY added_at", (user_id,)
            ).fetchall()
            return [row[0] for row in rows]


class closing_connection:
    """Контекстний менеджер: транзакція (commit/rollback) + гарантоване закриття з'єднання."""

    def __init__(self, db_file):
        self._conn = sqlite3.connect(db_file)

    def __enter__(self):
        self._conn.__enter__()
        return self._conn

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._conn.__exit__(exc_type, exc, tb)
        finally:
            self._conn.close()
