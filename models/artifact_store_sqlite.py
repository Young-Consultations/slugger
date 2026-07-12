"""SQLite-backed durable artifact store (CC-011).

Provides a file-backed artifact store that survives process restarts.
The schema is append-only: updates insert a new version row and the
latest version is served on read.

Corruption detection uses a per-row SHA-256 checksum.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from models.artifact import (
    Artifact,
    ArtifactMetadata,
    ArtifactStatus,
    ArtifactType,
    CodeArtifact,
    ConfigArtifact,
    DiagramArtifact,
    DocumentArtifact,
    TestArtifact,
)

_LOG = logging.getLogger(__name__)

_ARTIFACT_CLASSES: dict[str, type[Artifact]] = {
    ArtifactType.DOCUMENT.value: DocumentArtifact,
    ArtifactType.CODE.value: CodeArtifact,
    ArtifactType.TEST.value: TestArtifact,
    ArtifactType.CONFIG.value: ConfigArtifact,
    ArtifactType.DIAGRAM.value: DiagramArtifact,
}

_CREATE_ARTIFACTS_TABLE = """
CREATE TABLE IF NOT EXISTS artifacts (
    rowid        INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id  TEXT NOT NULL,
    name         TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    content      TEXT NOT NULL,
    status       TEXT NOT NULL,
    format       TEXT NOT NULL,
    tags         TEXT NOT NULL DEFAULT '[]',
    metadata     TEXT NOT NULL DEFAULT '{}',
    extra        TEXT NOT NULL DEFAULT '{}',
    checksum     TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_artifacts_artifact_id ON artifacts(artifact_id);
"""

_CREATE_DEDUP_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_artifacts_dedup
ON artifacts(artifact_id, checksum);
"""

_CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_SCHEMA_VERSION = 1


def _row_checksum(data: dict[str, Any]) -> str:
    """Compute a deterministic checksum of a row dict."""
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def _serialize(artifact: Artifact) -> dict[str, Any]:
    meta = artifact.metadata
    return {
        "artifact_id": artifact.artifact_id,
        "name": artifact.name,
        "artifact_type": artifact.artifact_type.value,
        "content": artifact.content,
        "status": artifact.status.value,
        "format": artifact.format,
        "tags": json.dumps(artifact.tags),
        "metadata": json.dumps(
            {
                "source_agent": meta.source_agent,
                "source_step": meta.source_step,
                "version": meta.version,
                "project_id": meta.project_id,
                "correlation_id": meta.correlation_id,
                "labels": meta.labels,
            }
        ),
        "extra": json.dumps(getattr(artifact, "extra", {})),
    }


def _deserialize(row: dict[str, Any]) -> Artifact | None:
    klass = _ARTIFACT_CLASSES.get(row["artifact_type"], DocumentArtifact)
    try:
        meta_data = json.loads(row.get("metadata", "{}"))
        meta = ArtifactMetadata(
            source_agent=meta_data.get("source_agent", ""),
            source_step=meta_data.get("source_step", ""),
            version=meta_data.get("version", "1.0.0"),
            project_id=meta_data.get("project_id"),
            correlation_id=meta_data.get("correlation_id"),
            labels=meta_data.get("labels", {}),
        )
        artifact = klass(
            artifact_id=row["artifact_id"],
            name=row["name"],
            content=row["content"],
            status=ArtifactStatus(row["status"]),
            format=row.get("format", "markdown"),
            tags=json.loads(row.get("tags", "[]")),
            metadata=meta,
        )
        extra = json.loads(row.get("extra", "{}"))
        if extra and hasattr(artifact, "extra"):
            artifact.extra.update(extra)
        return artifact
    except Exception as exc:  # noqa: BLE001
        _LOG.error("Failed to deserialize artifact %s: %s", row.get("artifact_id"), exc)
        return None


class SQLiteArtifactStore:
    """Durable, file-backed artifact store using SQLite.

    All writes append a new version row.  Reads return the latest version.
    Checksums detect storage corruption.
    """

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout = 30000")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_SCHEMA_VERSION_TABLE)
            version = (
                conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
                or 0
            )
            if version < 1:
                conn.execute(_CREATE_ARTIFACTS_TABLE)
                conn.execute(_CREATE_INDEX)
                conn.execute(_CREATE_DEDUP_INDEX)
                conn.execute(
                    "INSERT INTO schema_version(version) VALUES (?) ON CONFLICT(version) DO NOTHING",
                    (_SCHEMA_VERSION,),
                )

    def create(self, artifact: Artifact) -> Artifact:
        data = _serialize(artifact)
        data["checksum"] = _row_checksum(data)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO artifacts (artifact_id, name, artifact_type, content, status, format, tags, metadata, extra, checksum) "
                "VALUES (:artifact_id, :name, :artifact_type, :content, :status, :format, :tags, :metadata, :extra, :checksum)",
                data,
            )
        return artifact

    def get(self, artifact_id: str) -> Artifact | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM artifacts WHERE artifact_id = ? ORDER BY rowid DESC LIMIT 1",
                (artifact_id,),
            ).fetchone()
        if row is None:
            return None
        row_dict = dict(row)
        checksum = row_dict.pop("checksum", "")
        # Verify checksum (exclude rowid and created_at from data dict for compat)
        verify_dict = {
            k: v for k, v in row_dict.items() if k not in ("rowid", "created_at")
        }
        if checksum and _row_checksum(verify_dict) != checksum:
            _LOG.warning(
                "Checksum mismatch for artifact %s — possible corruption", artifact_id
            )
        return _deserialize(row_dict)

    def update(self, artifact: Artifact) -> Artifact:
        """Append a new version row (immutable append-only log)."""
        return self.create(artifact)

    def delete(self, artifact_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM artifacts WHERE artifact_id = ?", (artifact_id,))

    def list(self) -> list[Artifact]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT *, MAX(rowid) as max_rowid FROM artifacts GROUP BY artifact_id ORDER BY max_rowid DESC"
            ).fetchall()
        artifacts = []
        for row in rows:
            row_dict = {
                k: row[k]
                for k in row.keys()
                if k not in ("checksum", "rowid", "created_at", "max_rowid")
            }
            a = _deserialize(row_dict)
            if a is not None:
                artifacts.append(a)
        return artifacts

    def find_by_name(self, name: str) -> list[Artifact]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT *, MAX(rowid) as max_rowid FROM artifacts WHERE name = ? GROUP BY artifact_id ORDER BY max_rowid DESC",
                (name,),
            ).fetchall()
        artifacts = []
        for row in rows:
            row_dict = {
                k: row[k]
                for k in row.keys()
                if k not in ("checksum", "rowid", "created_at", "max_rowid")
            }
            a = _deserialize(row_dict)
            if a is not None:
                artifacts.append(a)
        return artifacts

    def extend(self, artifacts) -> None:
        for a in artifacts:
            self.create(a)

    def history(self, artifact_id: str) -> list[dict[str, Any]]:
        """Return all version rows for an artifact (for lineage queries)."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT rowid, artifact_id, name, status, created_at FROM artifacts WHERE artifact_id = ? ORDER BY rowid ASC",
                (artifact_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def schema_version(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT MAX(version) AS version FROM schema_version"
            ).fetchone()
        return int(row["version"] or 0)
