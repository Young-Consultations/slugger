"""Execution context models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from models.artifact import Artifact

if TYPE_CHECKING:
    from agents.messaging import MessageBus


class ExecutionState(str, Enum):
    """State of a runtime execution."""

    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


@dataclass(slots=True)
class ExecutionEvent:
    """Structured event generated during execution."""

    name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionContext:
    """Runtime context supplied to agents and engines."""

    project_id: str
    workflow_name: str
    step_name: str
    inputs: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)
    state: ExecutionState = ExecutionState.PENDING
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    events: list[ExecutionEvent] = field(default_factory=list)
    message_bus: MessageBus | None = field(default=None)

    def add_event(self, event: ExecutionEvent) -> None:
        """Attach an execution event to the context."""

        self.events.append(event)
