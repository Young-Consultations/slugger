"""Workflow State Database — SQLite-backed persistent workflow state.

:class:`WorkflowStateDB` provides a lightweight alternative to the JSON-file
:class:`~workflow.persistence.WorkflowPersistence` backend.  It stores
serialised :class:`~workflow.models.WorkflowInstance` records in a local
SQLite database, enabling efficient querying by status and time.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from workflow.models import WorkflowInstance
from workflow.persistence import _serialize_instance, _deserialize_instance


class WorkflowStateDB:
    """SQLite-backed store for :class:`~workflow.models.WorkflowInstance` records.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Use ``':memory:'`` for an
        in-process store (useful in tests).
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        # For in-memory databases we keep a single shared connection so data
        # is not lost between calls.  For file-backed databases a new
        # connection is opened per operation (safe for concurrent access).
        self._shared_conn: sqlite3.Connection | None = None
        if self._db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:")
            self._shared_conn.isolation_level = None
        self._initialise()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def _current_timestamp() -> str:
        """Return the current UTC timestamp as an ISO-8601 string."""
        return datetime.now(timezone.utc).isoformat()

    def save(self, instance: WorkflowInstance) -> None:
        """Upsert *instance* into the database."""
        payload = json.dumps(_serialize_instance(instance))
        now = self._current_timestamp()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs (run_id, workflow_name, status, payload, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = excluded.status,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    instance.run_id,
                    instance.definition.name,
                    instance.status,
                    payload,
                    now,
                ),
            )

    def load(self, run_id: str) -> WorkflowInstance | None:
        """Return the :class:`WorkflowInstance` for *run_id*, or ``None``."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT payload FROM workflow_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return _deserialize_instance(json.loads(row[0]))

    def list_runs(self, status: str | None = None) -> list[str]:
        """Return stored run IDs, optionally filtered by *status*."""
        with self._connection() as conn:
            if status is None:
                rows = conn.execute(
                    "SELECT run_id FROM workflow_runs ORDER BY updated_at"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT run_id FROM workflow_runs WHERE status = ? ORDER BY updated_at",
                    (status,),
                ).fetchall()
        return [row[0] for row in rows]

    def delete(self, run_id: str) -> None:
        """Remove the record for *run_id* from the database."""
        with self._connection() as conn:
            conn.execute("DELETE FROM workflow_runs WHERE run_id = ?", (run_id,))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _initialise(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id       TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    status       TEXT NOT NULL,
                    payload      TEXT NOT NULL,
                    updated_at   TEXT NOT NULL
                )
                """
            )

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        if self._shared_conn is not None:
            # In-memory: reuse the single shared connection
            yield self._shared_conn
        else:
            conn = sqlite3.connect(self._db_path)
            conn.isolation_level = None  # autocommit
            try:
                yield conn
            finally:
                conn.close()
