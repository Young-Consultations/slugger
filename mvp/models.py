"""Domain models for the narrow Slugger MVP execution path."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
import re
from typing import Any

SUPPORTED_TEMPLATES = frozenset({"cli"})
_PROJECT_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class MvpRunStatus(StrEnum):
    """Explicit lifecycle states for an MVP build run."""

    CREATED = "created"
    GENERATING = "generating"
    VALIDATING = "validating"
    TESTING = "testing"
    READY_TO_PUBLISH = "ready_to_publish"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    PUBLICATION_FAILED = "publication_failed"
    FAILED = "failed"


_ALLOWED_TRANSITIONS: dict[MvpRunStatus, frozenset[MvpRunStatus]] = {
    MvpRunStatus.CREATED: frozenset({MvpRunStatus.GENERATING, MvpRunStatus.FAILED}),
    MvpRunStatus.GENERATING: frozenset({MvpRunStatus.VALIDATING, MvpRunStatus.FAILED}),
    MvpRunStatus.VALIDATING: frozenset({MvpRunStatus.TESTING, MvpRunStatus.FAILED}),
    MvpRunStatus.TESTING: frozenset(
        {MvpRunStatus.READY_TO_PUBLISH, MvpRunStatus.FAILED}
    ),
    MvpRunStatus.READY_TO_PUBLISH: frozenset(
        {MvpRunStatus.PUBLISHING, MvpRunStatus.FAILED}
    ),
    MvpRunStatus.PUBLISHING: frozenset(
        {MvpRunStatus.COMPLETED, MvpRunStatus.PUBLICATION_FAILED}
    ),
    MvpRunStatus.PUBLICATION_FAILED: frozenset({MvpRunStatus.PUBLISHING}),
    MvpRunStatus.COMPLETED: frozenset(),
    MvpRunStatus.FAILED: frozenset(),
}


def _require_non_empty(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def validate_run_transition(current: MvpRunStatus, next_status: MvpRunStatus) -> None:
    """Raise when a run status transition is not allowed by the MVP lifecycle."""

    if next_status not in _ALLOWED_TRANSITIONS[current]:
        raise ValueError(
            f"Invalid MVP run transition: {current.value} -> {next_status.value}"
        )


@dataclass(frozen=True)
class MvpProjectRequest:
    """User input for building one generated MVP Python project."""

    idea: str
    project_name: str
    template: str
    github_repository: str
    base_branch: str = "main"

    def __post_init__(self) -> None:
        idea = _require_non_empty(self.idea, "idea")
        project_name = _require_non_empty(self.project_name, "project_name")
        template = _require_non_empty(self.template, "template")
        github_repository = _require_non_empty(
            self.github_repository, "github_repository"
        )
        base_branch = _require_non_empty(self.base_branch, "base_branch")

        if not _PROJECT_NAME_RE.fullmatch(project_name):
            raise ValueError(
                "project_name must be lowercase kebab-case starting with a letter"
            )
        if template not in SUPPORTED_TEMPLATES:
            raise ValueError(f"Unsupported MVP template: {template}")
        if not _REPOSITORY_RE.fullmatch(github_repository):
            raise ValueError("github_repository must be in owner/repository form")

        object.__setattr__(self, "idea", idea)
        object.__setattr__(self, "project_name", project_name)
        object.__setattr__(self, "template", template)
        object.__setattr__(self, "github_repository", github_repository)
        object.__setattr__(self, "base_branch", base_branch)


@dataclass(frozen=True)
class GeneratedFile:
    """One generated file recorded in a workspace inventory."""

    path: str
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        path = _require_non_empty(self.path, "path")
        sha256 = _require_non_empty(self.sha256, "sha256")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must be non-negative")
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True)
class GeneratedProjectInventory:
    """Inventory of files produced for an MVP run."""

    files: tuple[GeneratedFile, ...]
    inventory_hash: str

    def __post_init__(self) -> None:
        if not self.files:
            raise ValueError("files is required")
        inventory_hash = _require_non_empty(self.inventory_hash, "inventory_hash")
        object.__setattr__(self, "files", tuple(self.files))
        object.__setattr__(self, "inventory_hash", inventory_hash)


@dataclass(frozen=True)
class CheckResult:
    """Structured result from validation, installation, test, or smoke phases."""

    name: str
    passed: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_non_empty(self.name, "name"))


@dataclass(frozen=True)
class GitHubPublishResult:
    """Result of publishing a validated generated project to GitHub."""

    branch: str
    pull_request_url: str
    draft: bool = True
    existing: bool = False
    commit_sha: str | None = None
    pull_request_number: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "branch", _require_non_empty(self.branch, "branch"))
        object.__setattr__(
            self,
            "pull_request_url",
            _require_non_empty(self.pull_request_url, "pull_request_url"),
        )


@dataclass
class MvpRun:
    """Persistable state for one MVP build run."""

    run_id: str
    request: MvpProjectRequest
    status: MvpRunStatus = MvpRunStatus.CREATED
    workspace_path: str | None = None
    codex_session_id: str | None = None
    slugger_correlation_id: str | None = None
    prompt_version: str | None = None
    prompt_hash: str | None = None
    source_hash_before_codex: str | None = None
    source_hash_after_codex: str | None = None
    source_integrity_result: str | None = None
    changed_source_paths: tuple[str, ...] = ()
    publication_skipped: bool = False
    inventory: GeneratedProjectInventory | None = None
    validation_results: tuple[CheckResult, ...] = ()
    test_results: tuple[CheckResult, ...] = ()
    github_publish_result: GitHubPublishResult | None = None
    error_details: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.run_id = _require_non_empty(self.run_id, "run_id")
        self.status = MvpRunStatus(self.status)
        self.validation_results = tuple(self.validation_results)
        self.test_results = tuple(self.test_results)
        self.changed_source_paths = tuple(self.changed_source_paths)

    def transition_to(self, next_status: MvpRunStatus) -> None:
        next_status = MvpRunStatus(next_status)
        validate_run_transition(self.status, next_status)
        self.status = next_status
        self.updated_at = datetime.now(UTC)


@dataclass(frozen=True)
class MvpBuildResult:
    """Returned summary from the MVP build service."""

    run: MvpRun

    @property
    def status(self) -> MvpRunStatus:
        return self.run.status
