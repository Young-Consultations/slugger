"""Retry and escalation logic for failed agent tasks.

:class:`EscalationPolicy` describes when and how to escalate failures.
:class:`EscalationHandler` applies the policy and records escalation events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EscalationLevel(str, Enum):
    """Escalation severity levels."""

    RETRY = "retry"
    WARN = "warn"
    ESCALATE = "escalate"
    ABORT = "abort"


@dataclass
class EscalationPolicy:
    """Describes retry and escalation behaviour for a workflow step.

    Parameters
    ----------
    max_retries:
        Maximum number of automatic retries before escalating.
    escalation_level:
        Action taken after retries are exhausted.
    notify_agents:
        Agent names to notify on escalation.
    fallback_agent:
        Optional alternative agent to use after exhausting retries.
    metadata:
        Arbitrary extra policy configuration.
    """

    max_retries: int = 3
    escalation_level: EscalationLevel = EscalationLevel.ABORT
    notify_agents: list[str] = field(default_factory=list)
    fallback_agent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EscalationPolicy:
        raw_level = data.get("escalation_level", EscalationLevel.ABORT.value)
        try:
            level = EscalationLevel(raw_level)
        except ValueError:
            level = EscalationLevel.ABORT
        return cls(
            max_retries=int(data.get("max_retries", 3)),
            escalation_level=level,
            notify_agents=list(data.get("notify_agents", [])),
            fallback_agent=data.get("fallback_agent"),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "escalation_level": self.escalation_level.value,
            "notify_agents": list(self.notify_agents),
            "fallback_agent": self.fallback_agent,
            "metadata": dict(self.metadata),
        }


@dataclass
class EscalationEvent:
    """Records a single escalation occurrence.

    Parameters
    ----------
    step_name:
        Workflow step that failed.
    agent_name:
        Agent that was executing.
    attempt:
        Attempt number when escalation was triggered.
    level:
        Escalation level applied.
    reason:
        Human-readable failure reason.
    timestamp:
        UTC time of the escalation event.
    resolved:
        Whether the escalation was resolved (e.g. via fallback or manual fix).
    """

    step_name: str
    agent_name: str
    attempt: int
    level: EscalationLevel
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_name": self.step_name,
            "agent_name": self.agent_name,
            "attempt": self.attempt,
            "level": self.level.value,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
        }


class EscalationHandler:
    """Apply escalation policies and maintain an event log.

    Examples
    --------
    >>> handler = EscalationHandler()
    >>> policy = EscalationPolicy(max_retries=2, escalation_level=EscalationLevel.WARN)
    >>> level = handler.handle('generate_code', 'code_generator_agent', attempt=3, reason='timeout', policy=policy)
    >>> level
    <EscalationLevel.WARN: 'warn'>
    >>> len(handler.events())
    1
    """

    def __init__(self) -> None:
        self._events: list[EscalationEvent] = []

    def handle(
        self,
        step_name: str,
        agent_name: str,
        attempt: int,
        reason: str,
        policy: EscalationPolicy | None = None,
    ) -> EscalationLevel:
        """Evaluate the escalation *policy* for a failed step attempt.

        If *attempt* is within the retry budget, returns
        :attr:`~EscalationLevel.RETRY`.  Once retries are exhausted the
        configured ``escalation_level`` is returned and an
        :class:`EscalationEvent` is recorded.

        Parameters
        ----------
        step_name:
            Workflow step identifier.
        agent_name:
            Name of the failing agent.
        attempt:
            Current attempt number (1-based).
        reason:
            Brief description of the failure.
        policy:
            Policy to apply.  If ``None`` a default policy is used.

        Returns
        -------
        EscalationLevel
            The action that should be taken.
        """
        effective_policy = policy or EscalationPolicy()
        if attempt <= effective_policy.max_retries:
            level = EscalationLevel.RETRY
        else:
            level = effective_policy.escalation_level
            event = EscalationEvent(
                step_name=step_name,
                agent_name=agent_name,
                attempt=attempt,
                level=level,
                reason=reason,
            )
            self._events.append(event)
        return level

    def resolve(self, step_name: str) -> int:
        """Mark all open escalation events for *step_name* as resolved.

        Returns the number of events resolved.
        """
        count = 0
        for event in self._events:
            if event.step_name == step_name and not event.resolved:
                event.resolved = True
                count += 1
        return count

    def events(
        self, *, step_name: str | None = None, resolved: bool | None = None
    ) -> list[EscalationEvent]:
        """Return escalation events, optionally filtered.

        Parameters
        ----------
        step_name:
            Filter to a specific workflow step.
        resolved:
            If ``True`` return only resolved events; if ``False`` only open
            events; if ``None`` return all events.
        """
        result = self._events
        if step_name is not None:
            result = [e for e in result if e.step_name == step_name]
        if resolved is not None:
            result = [e for e in result if e.resolved == resolved]
        return list(result)

    def summary(self) -> dict[str, Any]:
        """Return a summary of escalation activity."""
        return {
            "total": len(self._events),
            "resolved": sum(1 for e in self._events if e.resolved),
            "open": sum(1 for e in self._events if not e.resolved),
            "by_level": {
                level.value: sum(1 for e in self._events if e.level == level)
                for level in EscalationLevel
            },
        }
