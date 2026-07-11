"""Human approval gate model and handler.

Provides configurable approval checkpoints that can pause a workflow until
a human (or automated process) grants approval.  An audit log records all
approval decisions for traceability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class ApprovalDecision(str, Enum):
    """Possible approval decisions."""

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    AUTO_APPROVED = 'auto_approved'


@dataclass
class ApprovalCheckpoint:
    """Configures an approval gate within a workflow step.

    Parameters
    ----------
    name:
        Unique name of the checkpoint (e.g. ``'pre-deployment'``).
    description:
        Human-readable description of what is being approved.
    required_approvers:
        List of approver identifiers required for approval.  An empty list
        means any approver is sufficient.
    auto_approve:
        When ``True`` the gate is automatically approved (useful in CI
        environments).
    timeout_seconds:
        Optional wall-clock timeout after which the gate auto-rejects if
        not yet approved.
    metadata:
        Arbitrary extra configuration for the checkpoint.
    """

    name: str
    description: str = ''
    required_approvers: list[str] = field(default_factory=list)
    auto_approve: bool = False
    timeout_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'required_approvers': list(self.required_approvers),
            'auto_approve': self.auto_approve,
            'timeout_seconds': self.timeout_seconds,
            'metadata': dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApprovalCheckpoint:
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            required_approvers=list(data.get('required_approvers', [])),
            auto_approve=bool(data.get('auto_approve', False)),
            timeout_seconds=data.get('timeout_seconds'),
            metadata=dict(data.get('metadata', {})),
        )


@dataclass(frozen=True)
class ApprovalRecord:
    """Record of a single approval decision.

    Each record is immutable once created.  :meth:`ApprovalGateHandler.approve`
    and :meth:`ApprovalGateHandler.reject` append *new* records rather than
    mutating existing ones, preserving the full decision history in the audit
    log.

    Parameters
    ----------
    record_id:
        Auto-generated UUID for the record.
    checkpoint_name:
        Name of the :class:`ApprovalCheckpoint` this record belongs to.
    run_id:
        Workflow run identifier.
    decision:
        The approval decision.
    approver:
        Identity of the approver (person or system).
    comment:
        Optional comment from the approver.
    timestamp:
        UTC time of the decision.
    """

    record_id: str = field(default_factory=lambda: str(uuid4()))
    checkpoint_name: str = ''
    run_id: str = ''
    decision: ApprovalDecision = ApprovalDecision.PENDING
    approver: str = 'system'
    comment: str = ''
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            'record_id': self.record_id,
            'checkpoint_name': self.checkpoint_name,
            'run_id': self.run_id,
            'decision': self.decision.value,
            'approver': self.approver,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat(),
        }


class ApprovalGateHandler:
    """Evaluate approval checkpoints and maintain an audit log.

    In auto-approve mode (``auto_approve=True`` on the checkpoint, or when
    ``force_auto_approve`` is set on the handler) all gates are immediately
    approved.

    Examples
    --------
    >>> handler = ApprovalGateHandler(force_auto_approve=True)
    >>> checkpoint = ApprovalCheckpoint(name='pre-release', description='Approve release')
    >>> record = handler.evaluate('run-1', checkpoint)
    >>> record.decision
    <ApprovalDecision.AUTO_APPROVED: 'auto_approved'>
    """

    def __init__(self, force_auto_approve: bool = False) -> None:
        self._force_auto = force_auto_approve
        self._audit: list[ApprovalRecord] = []
        self._resolved_ids: set[str] = set()

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        run_id: str,
        checkpoint: ApprovalCheckpoint,
        approver: str = 'system',
        comment: str = '',
    ) -> ApprovalRecord:
        """Evaluate *checkpoint* for *run_id*.

        If auto-approve is active the gate is immediately approved.
        Otherwise the record is stored with ``PENDING`` status and must be
        resolved via :meth:`approve` or :meth:`reject`.

        Returns
        -------
        ApprovalRecord
            The created approval record.
        """
        if self._force_auto or checkpoint.auto_approve:
            decision = ApprovalDecision.AUTO_APPROVED
            used_approver = approver or 'auto'
        else:
            decision = ApprovalDecision.PENDING
            used_approver = approver

        record = ApprovalRecord(
            checkpoint_name=checkpoint.name,
            run_id=run_id,
            decision=decision,
            approver=used_approver,
            comment=comment,
        )
        self._audit.append(record)
        return record

    def approve(self, record_id: str, approver: str, comment: str = '') -> ApprovalRecord:
        """Record an APPROVED decision for an existing PENDING record.

        The original PENDING record (identified by *record_id*) is retained
        in the audit log for full traceability.  A new
        :class:`ApprovalRecord` with its own ``record_id`` and ``APPROVED``
        status is appended and returned.  ``_resolved_ids`` tracks the
        original *record_id* so the same pending record cannot be resolved
        twice.

        Raises :exc:`KeyError` if *record_id* is not found.
        Raises :exc:`ValueError` if the record is not in PENDING state.
        """
        record = self._find(record_id)
        # First check catches non-PENDING records (e.g. AUTO_APPROVED).
        # Second check catches PENDING records that have already been resolved.
        if record.decision != ApprovalDecision.PENDING or record_id in self._resolved_ids:
            raise ValueError(f'Record {record_id!r} is not pending (current: {record.decision.value}).')
        new_record = ApprovalRecord(
            checkpoint_name=record.checkpoint_name,
            run_id=record.run_id,
            decision=ApprovalDecision.APPROVED,
            approver=approver,
            comment=comment,
        )
        self._audit.append(new_record)
        self._resolved_ids.add(record_id)
        return new_record

    def reject(self, record_id: str, approver: str, comment: str = '') -> ApprovalRecord:
        """Record a REJECTED decision for an existing PENDING record.

        The original PENDING record (identified by *record_id*) is retained
        in the audit log for full traceability.  A new
        :class:`ApprovalRecord` with its own ``record_id`` and ``REJECTED``
        status is appended and returned.  ``_resolved_ids`` tracks the
        original *record_id* so the same pending record cannot be resolved
        twice.

        Raises :exc:`KeyError` if *record_id* is not found.
        Raises :exc:`ValueError` if the record is not in PENDING state.
        """
        record = self._find(record_id)
        # First check catches non-PENDING records (e.g. AUTO_APPROVED).
        # Second check catches PENDING records that have already been resolved.
        if record.decision != ApprovalDecision.PENDING or record_id in self._resolved_ids:
            raise ValueError(f'Record {record_id!r} is not pending (current: {record.decision.value}).')
        new_record = ApprovalRecord(
            checkpoint_name=record.checkpoint_name,
            run_id=record.run_id,
            decision=ApprovalDecision.REJECTED,
            approver=approver,
            comment=comment,
        )
        self._audit.append(new_record)
        self._resolved_ids.add(record_id)
        return new_record

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_log(
        self,
        *,
        run_id: str | None = None,
        checkpoint_name: str | None = None,
        decision: ApprovalDecision | None = None,
    ) -> list[ApprovalRecord]:
        """Return audit records, optionally filtered."""
        records = self._audit
        if run_id is not None:
            records = [r for r in records if r.run_id == run_id]
        if checkpoint_name is not None:
            records = [r for r in records if r.checkpoint_name == checkpoint_name]
        if decision is not None:
            records = [r for r in records if r.decision == decision]
        return list(records)

    def summary(self) -> dict[str, Any]:
        """Return a summary of approval gate activity.

        Counts only active records (i.e., excludes original PENDING records
        that have since been resolved via :meth:`approve` or :meth:`reject`).
        Use :meth:`audit_log` to inspect the full decision history.
        """
        active = [r for r in self._audit if r.record_id not in self._resolved_ids]
        return {
            'total': len(active),
            'approved': sum(1 for r in active if r.decision == ApprovalDecision.APPROVED),
            'auto_approved': sum(1 for r in active if r.decision == ApprovalDecision.AUTO_APPROVED),
            'rejected': sum(1 for r in active if r.decision == ApprovalDecision.REJECTED),
            'pending': sum(1 for r in active if r.decision == ApprovalDecision.PENDING),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find(self, record_id: str) -> ApprovalRecord:
        for record in self._audit:
            if record.record_id == record_id:
                return record
        raise KeyError(f'Approval record not found: {record_id!r}')
