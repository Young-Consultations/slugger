"""SQLite persistence for MVP runs independent of legacy workflow storage."""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3
from typing import Any

from mvp.models import (
    CheckResult,
    GeneratedFile,
    GeneratedProjectInventory,
    GitHubPublishResult,
    MvpProjectRequest,
    MvpRun,
    MvpRunStatus,
)


class MvpRunRepositoryError(RuntimeError):
    """Raised when MVP run persistence cannot complete."""


class SQLiteMvpRunRepository:
    """Durable repository for MVP runs backed by one SQLite database."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def create(self, run: MvpRun) -> MvpRun:
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO mvp_runs (run_id, payload, status, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    _run_to_json(run),
                    run.status.value,
                    _datetime_to_text(run.updated_at),
                ),
            )
        return run

    def save(self, run: MvpRun) -> MvpRun:
        existing = self.get(run.run_id)
        if existing is None:
            return self.create(run)
        if existing.status != run.status:
            from mvp.models import validate_run_transition

            validate_run_transition(existing.status, run.status)
        run.updated_at = datetime.now(UTC)
        with self._connect() as db:
            db.execute(
                "UPDATE mvp_runs SET payload = ?, status = ?, updated_at = ? WHERE run_id = ?",
                (
                    _run_to_json(run),
                    run.status.value,
                    _datetime_to_text(run.updated_at),
                    run.run_id,
                ),
            )
        return run

    def transition(
        self, run_id: str, status: MvpRunStatus, *, error_details: str | None = None
    ) -> MvpRun:
        run = self.require(run_id)
        run.transition_to(status)
        if error_details is not None:
            run.error_details = error_details
        return self.save(run)

    def get(self, run_id: str) -> MvpRun | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT payload FROM mvp_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return _run_from_json(row[0])

    def require(self, run_id: str) -> MvpRun:
        run = self.get(run_id)
        if run is None:
            raise MvpRunRepositoryError(f"MVP run not found: {run_id}")
        return run

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS mvp_runs (
                    run_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)


def _run_to_json(run: MvpRun) -> str:
    payload = {
        "run_id": run.run_id,
        "request": asdict(run.request),
        "status": run.status.value,
        "workspace_path": run.workspace_path,
        "codex_session_id": run.codex_session_id,
        "slugger_correlation_id": run.slugger_correlation_id,
        "prompt_version": run.prompt_version,
        "prompt_hash": run.prompt_hash,
        "source_hash_before_codex": run.source_hash_before_codex,
        "source_hash_after_codex": run.source_hash_after_codex,
        "source_integrity_result": run.source_integrity_result,
        "changed_source_paths": list(run.changed_source_paths),
        "publication_skipped": run.publication_skipped,
        "inventory": _inventory_to_dict(run.inventory),
        "validation_results": [asdict(result) for result in run.validation_results],
        "test_results": [asdict(result) for result in run.test_results],
        "github_publish_result": asdict(run.github_publish_result)
        if run.github_publish_result
        else None,
        "error_details": run.error_details,
        "created_at": _datetime_to_text(run.created_at),
        "updated_at": _datetime_to_text(run.updated_at),
    }
    return json.dumps(payload, sort_keys=True)


def _run_from_json(raw: str) -> MvpRun:
    data: dict[str, Any] = json.loads(raw)
    inventory = data.get("inventory")
    github = data.get("github_publish_result")
    return MvpRun(
        run_id=data["run_id"],
        request=MvpProjectRequest(**data["request"]),
        status=MvpRunStatus(data["status"]),
        workspace_path=data.get("workspace_path"),
        codex_session_id=data.get("codex_session_id"),
        slugger_correlation_id=data.get("slugger_correlation_id"),
        prompt_version=data.get("prompt_version"),
        prompt_hash=data.get("prompt_hash"),
        source_hash_before_codex=data.get("source_hash_before_codex"),
        source_hash_after_codex=data.get("source_hash_after_codex"),
        source_integrity_result=data.get("source_integrity_result"),
        changed_source_paths=tuple(data.get("changed_source_paths", [])),
        publication_skipped=bool(data.get("publication_skipped", False)),
        inventory=_inventory_from_dict(inventory) if inventory else None,
        validation_results=tuple(
            CheckResult(**item) for item in data.get("validation_results", [])
        ),
        test_results=tuple(
            CheckResult(**item) for item in data.get("test_results", [])
        ),
        github_publish_result=GitHubPublishResult(**github) if github else None,
        error_details=data.get("error_details"),
        created_at=_datetime_from_text(data["created_at"]),
        updated_at=_datetime_from_text(data["updated_at"]),
    )


def _inventory_to_dict(
    inventory: GeneratedProjectInventory | None,
) -> dict[str, Any] | None:
    if inventory is None:
        return None
    return {
        "files": [asdict(file) for file in inventory.files],
        "inventory_hash": inventory.inventory_hash,
    }


def _inventory_from_dict(data: dict[str, Any]) -> GeneratedProjectInventory:
    return GeneratedProjectInventory(
        files=tuple(GeneratedFile(**item) for item in data["files"]),
        inventory_hash=data["inventory_hash"],
    )


def _datetime_to_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _datetime_from_text(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
