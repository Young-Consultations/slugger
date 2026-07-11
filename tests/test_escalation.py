"""Tests for Epic 2: escalation logic."""

from __future__ import annotations

import pytest

from workflow.escalation import (
    EscalationEvent,
    EscalationHandler,
    EscalationLevel,
    EscalationPolicy,
)


# ---------------------------------------------------------------------------
# Policy serialisation
# ---------------------------------------------------------------------------


def test_policy_to_dict_round_trip() -> None:
    policy = EscalationPolicy(
        max_retries=5,
        escalation_level=EscalationLevel.WARN,
        notify_agents=['pm_agent'],
        fallback_agent='backup_agent',
    )
    data = policy.to_dict()
    restored = EscalationPolicy.from_dict(data)
    assert restored.max_retries == 5
    assert restored.escalation_level == EscalationLevel.WARN
    assert 'pm_agent' in restored.notify_agents
    assert restored.fallback_agent == 'backup_agent'


def test_policy_from_dict_unknown_level_falls_back_to_abort() -> None:
    restored = EscalationPolicy.from_dict({'escalation_level': 'unknown'})
    assert restored.escalation_level == EscalationLevel.ABORT


# ---------------------------------------------------------------------------
# EscalationHandler.handle
# ---------------------------------------------------------------------------


def test_handle_within_retries_returns_retry() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=3, escalation_level=EscalationLevel.ABORT)
    level = handler.handle('step', 'agent', attempt=2, reason='timeout', policy=policy)
    assert level == EscalationLevel.RETRY


def test_handle_at_retry_limit_returns_policy_level() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=3, escalation_level=EscalationLevel.ESCALATE)
    level = handler.handle('step', 'agent', attempt=4, reason='error', policy=policy)
    assert level == EscalationLevel.ESCALATE


def test_handle_abort_after_retries_exhausted() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=1)
    level = handler.handle('step', 'agent', attempt=2, reason='fail', policy=policy)
    assert level == EscalationLevel.ABORT


def test_handle_records_event_after_retries() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=2)
    handler.handle('step', 'agent', attempt=3, reason='fail', policy=policy)
    events = handler.events()
    assert len(events) == 1
    assert events[0].step_name == 'step'
    assert events[0].reason == 'fail'


def test_handle_no_event_within_retries() -> None:
    handler = EscalationHandler()
    handler.handle('step', 'agent', attempt=1, reason='fail')
    assert handler.events() == []


def test_handle_default_policy_used_when_none() -> None:
    handler = EscalationHandler()
    # Default policy has max_retries=3
    level = handler.handle('step', 'agent', attempt=2, reason='fail', policy=None)
    assert level == EscalationLevel.RETRY


# ---------------------------------------------------------------------------
# Resolve
# ---------------------------------------------------------------------------


def test_resolve_marks_events_resolved() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=1)
    handler.handle('my-step', 'agent', attempt=2, reason='error', policy=policy)
    count = handler.resolve('my-step')
    assert count == 1
    assert handler.events(resolved=True)[0].step_name == 'my-step'


def test_resolve_returns_zero_if_nothing_to_resolve() -> None:
    handler = EscalationHandler()
    assert handler.resolve('nonexistent') == 0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_summary_counts() -> None:
    handler = EscalationHandler()
    policy = EscalationPolicy(max_retries=0, escalation_level=EscalationLevel.WARN)
    handler.handle('s1', 'a', attempt=1, reason='e1', policy=policy)
    handler.handle('s2', 'b', attempt=1, reason='e2', policy=policy)
    handler.resolve('s1')
    summary = handler.summary()
    assert summary['total'] == 2
    assert summary['resolved'] == 1
    assert summary['open'] == 1
    assert summary['by_level']['warn'] == 2
