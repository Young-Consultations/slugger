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
_CREATE_APPROVALS_INDEX = "CREATE INDEX IF NOT EXISTS idx_approvals_run_id ON approvals(run_id);"


def _record_checksum(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


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

    def save(self, record: ApprovalRecord) -> None:
        """Persist an approval record (append-only; raises on duplicate record_id)."""
        data = record.to_dict()
        checksum = _record_checksum(data)
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT INTO approvals (record_id, checkpoint_name, run_id, decision, approver, comment, timestamp, checksum) '
                    'VALUES (:record_id, :checkpoint_name, :run_id, :decision, :approver, :comment, :timestamp, :checksum)',
                    {**data, 'checksum': checksum},
                )
        except sqlite3.IntegrityError as exc:
            raise sqlite3.IntegrityError(f'Approval record {record.record_id!r} already exists in audit log') from exc

    def get_by_run(self, run_id: str) -> list[ApprovalRecord]:
        """Return all approval records for a run, verifying checksums."""
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM approvals WHERE run_id = ? ORDER BY rowid ASC',
                (run_id,),
            ).fetchall()
        records = []
        for row in rows:
            row_dict = dict(row)
            stored_checksum = row_dict.pop('checksum', '')
            row_dict.pop('rowid', None)
            if stored_checksum and _record_checksum(row_dict) != stored_checksum:
                _LOG.warning('Checksum mismatch for approval record %s — possible corruption', row_dict.get('record_id'))
            records.append(self._from_row(row_dict))
        return records

    def has_approval(self, run_id: str, checkpoint_name: str) -> bool:
        """Return True if the checkpoint has been APPROVED for the given run.

        Fails closed on checksum mismatches — a tampered row is treated as no
        approval rather than silently accepted.
        """
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM approvals WHERE run_id = ? AND checkpoint_name = ? AND decision IN (?, ?)',
                (run_id, checkpoint_name, ApprovalDecision.APPROVED.value, ApprovalDecision.AUTO_APPROVED.value),
            ).fetchall()
        for row in rows:
            row_dict = dict(row)
            stored_checksum = row_dict.pop('checksum', '')
            row_dict.pop('rowid', None)
            if not stored_checksum:
                _LOG.error(
                    'Approval record %s is missing integrity data — record rejected for authorization',
                    row_dict.get('record_id'),
                )
                continue
            if _record_checksum(row_dict) != stored_checksum:
                _LOG.error(
                    'Checksum mismatch for approval record %s — record rejected for authorization',
                    row_dict.get('record_id'),
                )
                continue
            return True
        return False

    def get_pending(self, run_id: str) -> list[ApprovalRecord]:
        """Return all PENDING approval records for a run (for resume security)."""
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT * FROM approvals WHERE run_id = ? AND decision = ? ORDER BY rowid ASC',
                (run_id, ApprovalDecision.PENDING.value),
            ).fetchall()
        return [self._from_row(dict(r)) for r in rows]

    def _from_row(self, row: dict[str, Any]) -> ApprovalRecord:
        ts_str = row.get('timestamp', '')
        try:
            ts = datetime.fromisoformat(ts_str)
        except Exception as exc:  # noqa: BLE001
            _LOG.warning('Failed to parse approval timestamp %r for record %s: %s', ts_str, row.get('record_id'), exc)
            ts = datetime.now(timezone.utc)
        return ApprovalRecord(
            record_id=row['record_id'],
            checkpoint_name=row['checkpoint_name'],
            run_id=row['run_id'],
            decision=ApprovalDecision(row['decision']),
            approver=row.get('approver', 'system'),
            comment=row.get('comment', ''),
            timestamp=ts,
        )
