"""Workflow runtime models."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any
from enum import Enum

from models.artifact import Artifact
from models.workflow import QualityGate, StepStatus


class WorkflowOutcome(str, Enum):
    """Evidence-backed outcome state for a completed workflow.

    This is distinct from the execution ``status`` (running/succeeded/failed).
    A workflow can ``succeed`` (all steps ran without errors) while still only
    producing placeholder artifacts. The outcome reflects what was actually
    delivered.

    Values are ordered: each level implies all prior levels were reached.
    """

    ARTIFACTS_GENERATED = "artifacts_generated"
    """Steps ran to completion and produced artifacts (possibly placeholder)."""

    VALIDATED = "validated"
    """All artifacts passed their quality gates."""

    PRODUCTION_READY = "production_ready"
    """Generated application was built, tested, and security-checked."""

    RELEASED = "released"
    """Application was published as a release candidate or production release."""


@dataclass(slots=True)
class ApprovalPolicy:
    """Inline approval policy for a workflow step (WP-022).

    Parameters
    ----------
    required_approvers:
        List of approver identifiers.  Empty means any approver is sufficient.
    auto_approve:
        Skip interactive approval in CI or testing environments.
    timeout_seconds:
        Seconds to wait before expiring the approval request.
    on_timeout:
        Action to take when the timeout expires: ``'abort'`` or ``'escalate'``.
    quorum:
        Minimum number of approvals required (0 = all required_approvers).
    """

    required_approvers: list[str] = field(default_factory=list)
    auto_approve: bool = False
    timeout_seconds: int = 3600
    on_timeout: str = "abort"
    quorum: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ApprovalPolicy:
        return cls(
            required_approvers=list(data.get("required_approvers", [])),
            auto_approve=bool(data.get("auto_approve", False)),
            timeout_seconds=int(data.get("timeout_seconds", 3600)),
            on_timeout=str(data.get("on_timeout", "abort")),
            quorum=int(data.get("quorum", 0)),
        )


@dataclass(slots=True)
class WorkflowStepDefinition:
    name: str
    agent: str
    description: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    quality_gates: list[QualityGate] = field(default_factory=list)
    retry_policy: dict[str, Any] = field(default_factory=dict)
    on_failure: str = "stop"
    approval_policy: ApprovalPolicy | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowDefinition:
    name: str
    version: str
    description: str = ""
    steps: list[WorkflowStepDefinition] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StepInstance:
    definition: WorkflowStepDefinition
    status: StepStatus = StepStatus.PENDING
    artifacts: list[Artifact] = field(default_factory=list)
    attempts: int = 0
    approval_record_id: str | None = None


@dataclass(slots=True)
class WorkflowInstance:
    definition: WorkflowDefinition
    step_instances: list[StepInstance] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    status: str = "pending"
    run_id: str = field(default_factory=lambda: str(uuid4()))
    outcome: WorkflowOutcome | None = None
    """Evidence-backed outcome; ``None`` until the workflow completes."""
