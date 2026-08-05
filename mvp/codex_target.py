"""Idempotency policy for organization-routed Codex execution.

The organization package validates the wire schema.  This module deliberately owns
only Slugger's target policy and durable GitHub ownership protocol.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Any, Protocol

SLUGGER_TARGET_REPOSITORY = "Young-Consultations/slugger"
SLUGGER_EXECUTOR = "codex"
SLUGGER_SUPPORTED_EXECUTION_MODES = frozenset({"verify", "implement"})
SLUGGER_SUPPORTED_PUBLICATION_MODES = frozenset({"draft_pr", "draft-pull-request"})
SLUGGER_ALLOWED_TASK_TYPES = frozenset({"mvp_python_cli", "python_cli", "slugger_mvp"})
SLUGGER_BASE_BRANCH = "main"
OWNERSHIP_MARKER_START = "<!-- slugger-canonical-delivery:"
OWNERSHIP_MARKER_END = "-->"


class TargetPolicyError(ValueError):
    """Raised when canonical input or managed repository state is unsafe."""


class DeliveryState(str, Enum):
    NEW = "new-delivery"
    RESUME = "resume-incomplete-delivery"
    REUSE = "reuse-completed-delivery"
    AMBIGUOUS = "ambiguous"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SluggerExecutionPlan:
    task_id: str
    delivery_id: str
    correlation_id: str
    publication_identity: str
    contract_version: str
    requested_branch: str
    base_branch: str
    mode: str
    idea: str
    project_name: str
    target_repository: str
    source_repository: str
    source_issue_number: int
    immutable_digest: str


@dataclass(frozen=True)
class ManagedPullRequest:
    number: int
    url: str
    state: str
    draft: bool
    head: str
    base: str
    body: str


@dataclass(frozen=True)
class PreflightResult:
    state: DeliveryState
    reason: str
    pull_request: ManagedPullRequest | None = None

    @property
    def run_codex(self) -> bool:
        return self.state in {DeliveryState.NEW, DeliveryState.RESUME}


class CanonicalRepository(Protocol):
    def branch_exists(self, branch: str) -> bool: ...
    def open_pull_requests(self) -> list[ManagedPullRequest]: ...
    def publish_branch(self, branch: str, base: str) -> None: ...
    def create_draft(
        self, *, branch: str, base: str, body: str
    ) -> ManagedPullRequest: ...


def _first(data: dict[str, Any], *names: str, default: Any = None) -> Any:
    return next((data[name] for name in names if name in data), default)


def _nested(data: dict[str, Any], *path: str) -> dict[str, Any]:
    value: Any = data
    for part in path:
        if not isinstance(value, dict):
            return {}
        value = value.get(part, {})
    return value if isinstance(value, dict) else {}


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TargetPolicyError(f"{name} is required")
    return value.strip()


def _require_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TargetPolicyError(f"{name} must be boolean")
    return value


def deterministic_branch(delivery_id: str) -> str:
    """Return Slugger's shared-contract branch for a canonical delivery."""

    identity = _require_text(delivery_id, "delivery_id")
    digest = hashlib.sha256(identity.encode()).hexdigest()[:20]
    return f"slugger/codex-delivery-{digest}"


def _immutable_digest(values: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(values, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def authorize_slugger_execution(
    execution_input: dict[str, Any],
) -> SluggerExecutionPlan:
    """Fail closed after canonical validation and preserve canonical identity."""

    target, source, task = (
        _nested(execution_input, "target"),
        _nested(execution_input, "source"),
        _nested(execution_input, "task"),
    )
    governance = _nested(execution_input, "governance") or task
    publication = _nested(execution_input, "publication")
    target_repository = _require_text(
        _first(target, "repository", "repository_full_name"), "target.repository"
    )
    if target_repository != SLUGGER_TARGET_REPOSITORY:
        raise TargetPolicyError("target repository must be Young-Consultations/slugger")
    if (
        _require_text(_first(target, "executor"), "target.executor").lower()
        != SLUGGER_EXECUTOR
    ):
        raise TargetPolicyError("executor must be Codex")
    source_repository = _require_text(
        _first(source, "repository", "repository_full_name"), "source.repository"
    )
    issue_number = _first(source, "issue_number", "issue")
    if not isinstance(issue_number, int) or issue_number <= 0:
        raise TargetPolicyError("source issue identity is required")
    if _first(source, "issue_state", "state") != "open":
        raise TargetPolicyError("source issue must be open")
    if not _require_bool(
        _first(governance, "approved", "explicitly_approved"), "approval"
    ):
        raise TargetPolicyError("source issue must remain explicitly approved")
    if _require_bool(
        _first(task, "sensitive", "is_sensitive", default=False), "sensitive"
    ):
        raise TargetPolicyError("sensitive work is not allowed for Slugger")
    if (
        _require_text(_first(task, "type", "task_type"), "task.type")
        not in SLUGGER_ALLOWED_TASK_TYPES
    ):
        raise TargetPolicyError("task type is not allowed for Slugger")
    mode = _require_text(
        _first(execution_input, "mode", "execution_mode", default=target.get("mode")),
        "execution mode",
    )
    if mode not in SLUGGER_SUPPORTED_EXECUTION_MODES:
        raise TargetPolicyError("execution mode is not supported")
    if (
        _require_text(
            _first(publication, "mode", "publication_mode"), "publication.mode"
        )
        not in SLUGGER_SUPPORTED_PUBLICATION_MODES
    ):
        raise TargetPolicyError("publication mode must be draft PR")
    if (
        _first(
            execution_input,
            "draft_pr_only",
            default=publication.get("draft_only", True),
        )
        is not True
    ):
        raise TargetPolicyError("draft_pr_only must be true")

    delivery_id = _require_text(
        _first(execution_input, "delivery_id", "idempotency_key"), "delivery_id"
    )
    contract_version = _require_text(
        _first(execution_input, "contract_version", "contract"), "contract_version"
    )
    requested_branch = _require_text(
        _first(execution_input, "requested_branch", default=publication.get("branch")),
        "requested_branch",
    )
    expected_branch = deterministic_branch(delivery_id)
    if requested_branch != expected_branch:
        raise TargetPolicyError(f"requested_branch must equal {expected_branch}")
    publication_identity = _require_text(
        _first(publication, "identity", "publication_identity"), "publication.identity"
    )
    if publication_identity != delivery_id:
        raise TargetPolicyError("publication identity must equal canonical delivery_id")
    correlation_id = _require_text(
        _first(execution_input, "correlation_id", default=task.get("correlation_id")),
        "correlation_id",
    )
    task_id = _require_text(_first(task, "id", "task_id"), "task.id")
    idea = _require_text(_first(task, "idea", "title", "summary"), "task.idea")
    project_name = _require_text(_first(task, "project_name"), "task.project_name")
    immutable = {
        "delivery_id": delivery_id,
        "correlation_id": correlation_id,
        "source_repository": source_repository,
        "source_issue_number": issue_number,
        "target_repository": target_repository,
        "requested_branch": requested_branch,
        "contract_version": contract_version,
        "task_id": task_id,
        "instructions": idea,
        "mode": mode,
    }
    return SluggerExecutionPlan(
        task_id,
        delivery_id,
        correlation_id,
        publication_identity,
        contract_version,
        requested_branch,
        SLUGGER_BASE_BRANCH,
        mode,
        idea,
        project_name,
        target_repository,
        source_repository,
        issue_number,
        _immutable_digest(immutable),
    )


def ownership_marker(plan: SluggerExecutionPlan) -> str:
    marker = {
        "schema": "slugger-canonical-delivery-v1",
        "delivery_id": plan.delivery_id,
        "correlation_id": plan.correlation_id,
        "source_issue": {
            "repository": plan.source_repository,
            "number": plan.source_issue_number,
        },
        "target_repository": plan.target_repository,
        "contract_version": plan.contract_version,
        "branch": plan.requested_branch,
        "base_branch": plan.base_branch,
        "publication_identity": plan.publication_identity,
        "immutable_digest": plan.immutable_digest,
    }
    return f"{OWNERSHIP_MARKER_START}{json.dumps(marker, sort_keys=True)}{OWNERSHIP_MARKER_END}"


def parse_ownership_marker(body: str) -> dict[str, Any]:
    matches = re.findall(
        re.escape(OWNERSHIP_MARKER_START) + r"(.*?)" + re.escape(OWNERSHIP_MARKER_END),
        body,
        re.DOTALL,
    )
    if len(matches) != 1:
        return {}
    try:
        value = json.loads(matches[0].strip())
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _marker_matches(plan: SluggerExecutionPlan, marker: dict[str, Any]) -> bool:
    return marker == json.loads(
        ownership_marker(plan)[len(OWNERSHIP_MARKER_START) : -len(OWNERSHIP_MARKER_END)]
    )


def preflight(
    plan: SluggerExecutionPlan, repository: CanonicalRepository
) -> PreflightResult:
    """Classify durable state without mutating or trusting branch names alone."""

    prs = repository.open_pull_requests()
    claimed = [
        pr
        for pr in prs
        if parse_ownership_marker(pr.body).get("delivery_id") == plan.delivery_id
    ]
    branch_prs = [pr for pr in prs if pr.head == plan.requested_branch]
    candidates = {pr.number: pr for pr in claimed + branch_prs}
    if len(candidates) > 1:
        return PreflightResult(
            DeliveryState.AMBIGUOUS, "multiple matching pull requests"
        )
    if candidates:
        pr = next(iter(candidates.values()))
        marker = parse_ownership_marker(pr.body)
        if not marker or not _marker_matches(plan, marker):
            return PreflightResult(
                DeliveryState.AMBIGUOUS,
                "ownership marker conflicts with canonical input",
                pr,
            )
        if (
            pr.state.lower() != "open"
            or not pr.draft
            or pr.base != plan.base_branch
            or pr.head != plan.requested_branch
        ):
            return PreflightResult(
                DeliveryState.AMBIGUOUS, "managed pull request shape is unsafe", pr
            )
        return PreflightResult(
            DeliveryState.REUSE, "completed managed draft already exists", pr
        )
    if repository.branch_exists(plan.requested_branch):
        return PreflightResult(
            DeliveryState.BLOCKED,
            "branch exists but delivery ownership cannot be proven",
        )
    return PreflightResult(DeliveryState.NEW, "no managed state exists")


def publish_after_codex(
    plan: SluggerExecutionPlan, repository: CanonicalRepository
) -> PreflightResult:
    """Publish once, converging on a valid winner after a create race.

    The backend must make ``publish_branch`` a create-only operation.  A conflict is
    never treated as permission to force-push: repository state is reclassified.
    """

    before = preflight(plan, repository)
    if before.state is DeliveryState.REUSE:
        return before
    if before.state is not DeliveryState.NEW:
        return before
    try:
        repository.publish_branch(plan.requested_branch, plan.base_branch)
        pr = repository.create_draft(
            branch=plan.requested_branch,
            base=plan.base_branch,
            body=ownership_marker(plan),
        )
        return PreflightResult(DeliveryState.RESUME, "delivery safely published", pr)
    except Exception:
        # GitHub reports branch/PR create races through several status codes.  The
        # only safe recovery is structural validation of the durable winner.
        recovered = preflight(plan, repository)
        if recovered.state is DeliveryState.REUSE:
            return recovered
        return PreflightResult(
            DeliveryState.AMBIGUOUS,
            "publication conflict did not converge on one owned draft",
            recovered.pull_request,
        )
