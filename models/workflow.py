"""Workflow domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StepStatus(str, Enum):
    """Execution status for a workflow step."""

    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    AWAITING_APPROVAL = 'awaiting_approval'


@dataclass(slots=True)
class QualityGate:
    """Validation checkpoint applied to a step."""

    validator: str
    name: str | None = None
    condition: str | None = None
    required: bool = True
    config: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowStep:
    """Single executable step in a workflow."""

    name: str
    agent: str
    description: str = ''
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    quality_gates: list[QualityGate] = field(default_factory=list)
    retry_policy: dict[str, object] = field(default_factory=dict)
    on_failure: str = 'stop'
    metadata: dict[str, object] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING


@dataclass(slots=True)
class Workflow:
    """Declarative workflow definition."""

    name: str
    version: str
    description: str = ''
    steps: list[WorkflowStep] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
