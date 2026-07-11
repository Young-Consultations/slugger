"""Tests for Epic 4: human approval gates."""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta

import pytest

from workflow.approvals import (
    ApprovalCheckpoint,
    ApprovalDecision,
    ApprovalGateHandler,
    ApprovalRecord,
)


# ---------------------------------------------------------------------------
# ApprovalCheckpoint
# ---------------------------------------------------------------------------


def test_checkpoint_to_dict_round_trip() -> None:
    cp = ApprovalCheckpoint(
        name='pre-deploy',
        description='Approve deployment',
        required_approvers=['alice', 'bob'],
        auto_approve=False,
        timeout_seconds=3600,
    )
    data = cp.to_dict()
    restored = ApprovalCheckpoint.from_dict(data)
    assert restored.name == 'pre-deploy'
    assert restored.required_approvers == ['alice', 'bob']
    assert restored.timeout_seconds == 3600
    assert restored.auto_approve is False


# ---------------------------------------------------------------------------
# Auto-approve
# ---------------------------------------------------------------------------


def test_auto_approve_via_checkpoint_flag() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', auto_approve=True)
    record = handler.evaluate('run-1', cp)
    assert record.decision == ApprovalDecision.AUTO_APPROVED


def test_auto_approve_via_handler_flag() -> None:
    handler = ApprovalGateHandler(force_auto_approve=True)
    cp = ApprovalCheckpoint(name='gate', auto_approve=False)
    record = handler.evaluate('run-1', cp)
    assert record.decision == ApprovalDecision.AUTO_APPROVED


def test_non_auto_approve_creates_pending_record() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', auto_approve=False)
    record = handler.evaluate('run-2', cp)
    assert record.decision == ApprovalDecision.PENDING


# ---------------------------------------------------------------------------
# Approve / reject
# ---------------------------------------------------------------------------


def test_approve_pending_record() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='deploy', auto_approve=False)
    record = handler.evaluate('run-1', cp)
    approved = handler.approve(record.record_id, approver='alice', comment='LGTM')
    assert approved.decision == ApprovalDecision.APPROVED
    assert approved.approver == 'alice'
    assert approved.comment == 'LGTM'


def test_reject_pending_record() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='deploy', auto_approve=False)
    record = handler.evaluate('run-1', cp)
    rejected = handler.reject(record.record_id, approver='bob', comment='Needs work')
    assert rejected.decision == ApprovalDecision.REJECTED


def test_approve_already_approved_raises() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', auto_approve=True)
    record = handler.evaluate('run-1', cp)
    with pytest.raises(ValueError, match='not pending'):
        handler.approve(record.record_id, approver='x')


def test_reject_already_rejected_raises() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', auto_approve=False)
    record = handler.evaluate('run-1', cp)
    handler.reject(record.record_id, approver='x')
    with pytest.raises(ValueError, match='not pending'):
        handler.reject(record.record_id, approver='y')


def test_approve_unknown_id_raises() -> None:
    handler = ApprovalGateHandler()
    with pytest.raises(KeyError):
        handler.approve('nonexistent-id', approver='x')


def test_required_approvers_are_enforced_on_approve() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', required_approvers=['alice'])
    record = handler.evaluate('run-1', cp)
    with pytest.raises(ValueError, match='not allowed'):
        handler.approve(record.record_id, approver='bob')


def test_timeout_auto_rejects_pending_record() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', timeout_seconds=1)
    record = handler.evaluate('run-1', cp)
    handler._audit[-1] = replace(handler._audit[-1], timestamp=handler._audit[-1].timestamp - timedelta(seconds=5))
    with pytest.raises(ValueError, match='not pending'):
        handler.approve(record.record_id, approver='alice')
    rejected = handler.audit_log(decision=ApprovalDecision.REJECTED)
    assert len(rejected) == 1
    assert rejected[0].approver == 'system'
    assert 'timed out' in rejected[0].comment


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------


def test_audit_log_contains_all_records() -> None:
    handler = ApprovalGateHandler(force_auto_approve=True)
    cp = ApprovalCheckpoint(name='gate')
    handler.evaluate('run-1', cp)
    handler.evaluate('run-2', cp)
    assert len(handler.audit_log()) == 2


def test_audit_log_filter_by_run() -> None:
    handler = ApprovalGateHandler(force_auto_approve=True)
    cp = ApprovalCheckpoint(name='gate')
    handler.evaluate('run-A', cp)
    handler.evaluate('run-B', cp)
    assert len(handler.audit_log(run_id='run-A')) == 1


def test_audit_log_filter_by_decision() -> None:
    handler = ApprovalGateHandler()
    cp = ApprovalCheckpoint(name='gate', auto_approve=False)
    record = handler.evaluate('run-1', cp)
    handler.approve(record.record_id, approver='alice')
    cp2 = ApprovalCheckpoint(name='gate2', auto_approve=True)
    handler.evaluate('run-2', cp2)
    approved = handler.audit_log(decision=ApprovalDecision.APPROVED)
    assert len(approved) == 1


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_summary_counts() -> None:
    handler = ApprovalGateHandler()
    cp_auto = ApprovalCheckpoint(name='auto', auto_approve=True)
    cp_manual = ApprovalCheckpoint(name='manual', auto_approve=False)
    handler.evaluate('r1', cp_auto)
    record = handler.evaluate('r2', cp_manual)
    handler.approve(record.record_id, approver='alice')
    record2 = handler.evaluate('r3', cp_manual)
    handler.reject(record2.record_id, approver='bob')
    summary = handler.summary()
    assert summary['total'] == 3
    assert summary['auto_approved'] == 1
    assert summary['approved'] == 1
    assert summary['rejected'] == 1
    assert summary['pending'] == 0
