"""Workflow runtime models."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any

from models.artifact import Artifact
from models.workflow import QualityGate, StepStatus


@dataclass(slots=True)
class WorkflowStepDefinition:
    name: str
    agent: str
    description: str = ''
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    quality_gates: list[QualityGate] = field(default_factory=list)
    retry_policy: dict[str, Any] = field(default_factory=dict)
    on_failure: str = 'stop'
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowDefinition:
    name: str
    version: str
    description: str = ''
    steps: list[WorkflowStepDefinition] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StepInstance:
    definition: WorkflowStepDefinition
    status: StepStatus = StepStatus.PENDING
    artifacts: list[Artifact] = field(default_factory=list)
    attempts: int = 0


@dataclass(slots=True)
class WorkflowInstance:
    definition: WorkflowDefinition
    step_instances: list[StepInstance] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    status: str = 'pending'
    run_id: str = field(default_factory=lambda: str(uuid4()))
