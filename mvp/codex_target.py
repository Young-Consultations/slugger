"""Slugger target policy for organization-routed Codex execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SLUGGER_TARGET_REPOSITORY = "Young-Consultations/slugger"
SLUGGER_EXECUTOR = "codex"
SLUGGER_SUPPORTED_EXECUTION_MODES = frozenset({"verify", "implement"})
SLUGGER_SUPPORTED_PUBLICATION_MODES = frozenset({"draft_pr", "draft-pull-request"})
SLUGGER_ALLOWED_TASK_TYPES = frozenset({"mvp_python_cli", "python_cli", "slugger_mvp"})


class TargetPolicyError(ValueError):
    """Raised when canonical input fails Slugger-specific target policy."""


@dataclass(frozen=True)
class SluggerExecutionPlan:
    """Authorized Slugger execution details derived from canonical input."""

    task_id: str
    correlation_id: str
    publication_identity: str
    mode: str
    idea: str
    project_name: str
    target_repository: str
    source_repository: str
    source_issue_number: int


def _first(data: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in data:
            return data[name]
    return default


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


def authorize_slugger_execution(
    execution_input: dict[str, Any],
) -> SluggerExecutionPlan:
    """Apply Slugger-only policy after organization canonical validation.

    The organization execution input is the source of truth.  This function does not
    parse issue bodies or recreate canonical identities; it only rejects inputs that
    Slugger is not allowed to execute.
    """

    target = _nested(execution_input, "target")
    source = _nested(execution_input, "source")
    task = _nested(execution_input, "task")
    governance = _nested(execution_input, "governance") or task
    publication = _nested(execution_input, "publication")

    target_repository = _require_text(
        _first(target, "repository", "repository_full_name"), "target.repository"
    )
    if target_repository != SLUGGER_TARGET_REPOSITORY:
        raise TargetPolicyError("target repository must be Young-Consultations/slugger")

    executor = _require_text(_first(target, "executor"), "target.executor").lower()
    if executor != SLUGGER_EXECUTOR:
        raise TargetPolicyError("executor must be Codex")

    source_repository = _require_text(
        _first(source, "repository", "repository_full_name"), "source.repository"
    )
    issue_number = _first(source, "issue_number", "issue")
    if not isinstance(issue_number, int) or issue_number <= 0:
        raise TargetPolicyError("source issue identity is required")
    if _first(source, "issue_state", "state") != "open":
        raise TargetPolicyError("source issue must be open")
    if (
        _require_bool(_first(governance, "approved", "explicitly_approved"), "approval")
        is not True
    ):
        raise TargetPolicyError("source issue must remain explicitly approved")
    if _require_bool(
        _first(task, "sensitive", "is_sensitive", default=False), "sensitive"
    ):
        raise TargetPolicyError("sensitive work is not allowed for Slugger")

    task_type = _require_text(_first(task, "type", "task_type"), "task.type")
    if task_type not in SLUGGER_ALLOWED_TASK_TYPES:
        raise TargetPolicyError("task type is not allowed for Slugger")

    mode = _require_text(
        _first(execution_input, "mode", "execution_mode", default=target.get("mode")),
        "execution mode",
    )
    if mode not in SLUGGER_SUPPORTED_EXECUTION_MODES:
        raise TargetPolicyError("execution mode is not supported")

    publication_mode = _require_text(
        _first(publication, "mode", "publication_mode"), "publication.mode"
    )
    if publication_mode not in SLUGGER_SUPPORTED_PUBLICATION_MODES:
        raise TargetPolicyError("publication mode must be draft PR")

    task_id = _require_text(_first(task, "id", "task_id"), "task.id")
    correlation_id = _require_text(
        _first(execution_input, "correlation_id", default=task.get("correlation_id")),
        "correlation_id",
    )
    publication_identity = _require_text(
        _first(publication, "identity", "publication_identity"), "publication.identity"
    )

    return SluggerExecutionPlan(
        task_id=task_id,
        correlation_id=correlation_id,
        publication_identity=publication_identity,
        mode=mode,
        idea=_require_text(_first(task, "idea", "title", "summary"), "task.idea"),
        project_name=_require_text(_first(task, "project_name"), "task.project_name"),
        target_repository=target_repository,
        source_repository=source_repository,
        source_issue_number=issue_number,
    )
