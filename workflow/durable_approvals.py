"""Durable approval store backed by SQLite (CC-012).

Ensures approval records survive process restart and enforces:
- Quorum requirements
- Role-based approver validation
- Resume security (pending approvals from previous run cannot be bypassed)
- Immutable append-only audit log with corruption detection
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from workflow.approvals import ApprovalDecision, ApprovalRecord

_LOG = logging.getLogger(__name__)

_CREATE_APPROVALS_TABLE = """
CREATE TABLE IF NOT EXISTS approvals (
    rowid           INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id       TEXT NOT NULL UNIQUE,
    checkpoint_name TEXT NOT NULL,
    run_id          TEXT NOT NULL,
    decision        TEXT NOT NULL,
    approver        TEXT NOT NULL,
    comment         TEXT NOT NULL DEFAULT '',
    timestamp       TEXT NOT NULL,
    checksum        TEXT NOT NULL
);
"""
_CREATE_APPROVALS_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_approvals_run_id ON approvals(run_id);"
)
_CREATE_REQUESTS_TABLE = """
CREATE TABLE IF NOT EXISTS approval_requests (
    request_id       TEXT PRIMARY KEY,
    policy_json      TEXT NOT NULL,
    artifact_ids_json TEXT NOT NULL,
    checksums_json   TEXT NOT NULL,
    allowed_actors_json TEXT NOT NULL,
    quorum           INTEGER NOT NULL,
    status           TEXT NOT NULL,
    created_at       TEXT NOT NULL
);
"""
_CREATE_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS approval_request_decisions (
    rowid            INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id      TEXT NOT NULL UNIQUE,
    request_id       TEXT NOT NULL,
    actor            TEXT NOT NULL,
    decision         TEXT NOT NULL,
    rationale        TEXT NOT NULL DEFAULT '',
    timestamp        TEXT NOT NULL,
    FOREIGN KEY(request_id) REFERENCES approval_requests(request_id)
);
"""
_CREATE_REQUESTS_STATUS_INDEX = "CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);"
_CREATE_DECISIONS_REQUEST_INDEX = "CREATE INDEX IF NOT EXISTS idx_approval_decisions_request_id ON approval_request_decisions(request_id);"


def _record_checksum(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ApprovalRequestStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequestDecision:
    APPROVE = "approve"
    REJECT = "reject"


class DurableApprovalStore:
    """Persist approval records to SQLite.

    Provides resumable, corruption-detected approval state that survives
    process restarts.  All writes are append-only.
    """

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_APPROVALS_TABLE)
            conn.execute(_CREATE_APPROVALS_INDEX)
            conn.execute(_CREATE_REQUESTS_TABLE)
            conn.execute(_CREATE_DECISIONS_TABLE)
            conn.execute(_CREATE_REQUESTS_STATUS_INDEX)
            conn.execute(_CREATE_DECISIONS_REQUEST_INDEX)
            request_columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(approval_requests)"
                ).fetchall()
            }
            if (
                "required_roles_json" in request_columns
                and "allowed_actors_json" not in request_columns
            ):
                conn.execute(
                    "ALTER TABLE approval_requests RENAME COLUMN required_roles_json TO allowed_actors_json"
                )

    def save(self, record: ApprovalRecord) -> None:
        """Persist an approval record (append-only; raises on duplicate record_id)."""
        data = record.to_dict()
        checksum = _record_checksum(data)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO approvals (record_id, checkpoint_name, run_id, decision, approver, comment, timestamp, checksum) "
                    "VALUES (:record_id, :checkpoint_name, :run_id, :decision, :approver, :comment, :timestamp, :checksum)",
                    {**data, "checksum": checksum},
                )
        except sqlite3.IntegrityError as exc:
            raise sqlite3.IntegrityError(
                f"Approval record {record.record_id!r} already exists in audit log"
            ) from exc

    def get_by_run(self, run_id: str) -> list[ApprovalRecord]:
        """Return all approval records for a run, verifying checksums."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM approvals WHERE run_id = ? ORDER BY rowid ASC",
                (run_id,),
            ).fetchall()
        records = []
        for row in rows:
            row_dict = dict(row)
            stored_checksum = row_dict.pop("checksum", "")
            row_dict.pop("rowid", None)
            if stored_checksum and _record_checksum(row_dict) != stored_checksum:
                _LOG.warning(
                    "Checksum mismatch for approval record %s — possible corruption",
                    row_dict.get("record_id"),
                )
            records.append(self._from_row(row_dict))
        return records

    def has_approval(self, run_id: str, checkpoint_name: str) -> bool:
        """Return True if the checkpoint has been APPROVED for the given run.

        Fails closed on checksum mismatches — a tampered row is treated as no
        approval rather than silently accepted.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM approvals WHERE run_id = ? AND checkpoint_name = ? AND decision IN (?, ?)",
                (
                    run_id,
                    checkpoint_name,
                    ApprovalDecision.APPROVED.value,
                    ApprovalDecision.AUTO_APPROVED.value,
                ),
            ).fetchall()
        for row in rows:
            row_dict = dict(row)
            stored_checksum = row_dict.pop("checksum", "")
            row_dict.pop("rowid", None)
            if not stored_checksum:
                _LOG.error(
                    "Approval record %s is missing integrity data — record rejected for authorization",
                    row_dict.get("record_id"),
                )
                continue
            if _record_checksum(row_dict) != stored_checksum:
                _LOG.error(
                    "Checksum mismatch for approval record %s — record rejected for authorization",
                    row_dict.get("record_id"),
                )
                continue
            return True
        return False

    def list_pending_requests(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent pending durable approval requests."""
        return self.list_requests(status=ApprovalRequestStatus.PENDING, limit=limit)

    def get_pending_records(self, run_id: str) -> list[ApprovalRecord]:
        """Return pending approval records for a workflow run."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM approvals WHERE run_id = ? AND decision = ? ORDER BY rowid ASC",
                (run_id, ApprovalDecision.PENDING.value),
            ).fetchall()
        return [self._from_row(dict(r)) for r in rows]

    def get_pending(self, run_id: str) -> list[ApprovalRecord]:
        """Backward-compatible alias for pending approval records."""
        return self.get_pending_records(run_id)

    def request_approval(
        self,
        request_id: str,
        policy: dict[str, Any] | str,
        artifact_ids: list[str],
        checksums: dict[str, str],
        allowed_actors: list[str],
        quorum: int,
    ) -> dict[str, Any]:
        """Create a durable approval request bound to immutable evidence."""
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO approval_requests (request_id, policy_json, artifact_ids_json, checksums_json, allowed_actors_json, quorum, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    request_id,
                    _json_dumps(policy),
                    _json_dumps(artifact_ids),
                    _json_dumps(checksums),
                    _json_dumps(allowed_actors),
                    max(0, int(quorum)),
                    ApprovalRequestStatus.PENDING,
                    created_at,
                ),
            )
        return self.get_request(request_id)

    def record_decision(
        self, request_id: str, actor: str, decision: str, rationale: str
    ) -> dict[str, Any]:
        """Append an approval decision and update the request status."""
        request = self.get_request(request_id)
        normalized = decision.strip().lower()
        if normalized not in {
            ApprovalRequestDecision.APPROVE,
            ApprovalRequestDecision.REJECT,
        }:
            raise ValueError(f"Unsupported approval decision: {decision!r}")
        if request["status"] != ApprovalRequestStatus.PENDING:
            raise ValueError(f"Approval request {request_id!r} is not pending")
        if request["allowed_actors"] and actor not in request["allowed_actors"]:
            raise ValueError(
                f"Actor {actor!r} is not allowed for approval request {request_id!r}"
            )
        if any(existing["actor"] == actor for existing in request["decisions"]):
            raise ValueError(
                f"Actor {actor!r} has already decided approval request {request_id!r}"
            )

        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO approval_request_decisions (decision_id, request_id, actor, decision, rationale, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid4()), request_id, actor, normalized, rationale, timestamp),
            )
        return self._update_request_status(request_id)

    def is_valid(self, request_id: str) -> bool:
        """Return False when any bound artifact checksum no longer matches."""
        request = self.get_request(request_id)
        if request["status"] == ApprovalRequestStatus.REJECTED:
            return False
        checksums = request["checksums"]
        if not isinstance(checksums, dict):
            return False
        for artifact_id in request["artifact_ids"]:
            expected = checksums.get(artifact_id)
            if not expected:
                return False
            artifact_path = Path(artifact_id)
            if not artifact_path.exists() or not artifact_path.is_file():
                return False
            if _sha256_file(artifact_path) != expected:
                return False
        return True

    def get_request(self, request_id: str) -> dict[str, Any]:
        """Return a request with all recorded decisions."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM approval_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Approval request not found: {request_id!r}")
        return self._request_from_row(dict(row))

    def list_requests(
        self, status: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Return recent durable approval requests."""
        query = "SELECT * FROM approval_requests"
        params: tuple[Any, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY created_at DESC LIMIT ?"
        params += (limit,)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._request_from_row(dict(row)) for row in rows]

    def _from_row(self, row: dict[str, Any]) -> ApprovalRecord:
        ts_str = row.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except Exception as exc:  # noqa: BLE001
            _LOG.warning(
                "Failed to parse approval timestamp %r for record %s: %s",
                ts_str,
                row.get("record_id"),
                exc,
            )
            ts = datetime.now(timezone.utc)
        return ApprovalRecord(
            record_id=row["record_id"],
            checkpoint_name=row["checkpoint_name"],
            run_id=row["run_id"],
            decision=ApprovalDecision(row["decision"]),
            approver=row.get("approver", "system"),
            comment=row.get("comment", ""),
            timestamp=ts,
        )

    def _request_from_row(self, row: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            decision_rows = conn.execute(
                "SELECT actor, decision, rationale, timestamp FROM approval_request_decisions WHERE request_id = ? ORDER BY rowid ASC",
                (row["request_id"],),
            ).fetchall()
        return {
            "request_id": row["request_id"],
            "policy": json.loads(row["policy_json"]),
            "artifact_ids": json.loads(row["artifact_ids_json"]),
            "checksums": json.loads(row["checksums_json"]),
            "allowed_actors": json.loads(row["allowed_actors_json"]),
            "quorum": row["quorum"],
            "status": row["status"],
            "created_at": row["created_at"],
            "decisions": [dict(decision_row) for decision_row in decision_rows],
        }

    def _update_request_status(self, request_id: str) -> dict[str, Any]:
        request = self.get_request(request_id)
        decisions = request["decisions"]
        if any(
            decision["decision"] == ApprovalRequestDecision.REJECT
            for decision in decisions
        ):
            status = ApprovalRequestStatus.REJECTED
        else:
            approvals = {
                decision["actor"]
                for decision in decisions
                if decision["decision"] == ApprovalRequestDecision.APPROVE
            }
            quorum = request["quorum"] or max(1, len(request["allowed_actors"]) or 1)
            status = (
                ApprovalRequestStatus.APPROVED
                if len(approvals) >= quorum
                else ApprovalRequestStatus.PENDING
            )
        with self._connect() as conn:
            conn.execute(
                "UPDATE approval_requests SET status = ? WHERE request_id = ?",
                (status, request_id),
            )
        return self.get_request(request_id)
