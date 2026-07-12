"""GitHub service models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GitHubRepo:
    owner: str
    name: str
    default_branch: str = "main"


@dataclass(slots=True)
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str = "open"
    labels: list[str] = field(default_factory=list)
    milestone_number: int | None = None


@dataclass(slots=True)
class GitHubPR:
    number: int
    title: str
    body: str
    state: str = "open"
    head: str = ""
    base: str = "main"
    draft: bool = False
    merged: bool = False
    milestone_number: int | None = None


@dataclass(slots=True)
class GitHubComment:
    author: str
    body: str


@dataclass(slots=True)
class GitHubMilestone:
    """Represents a GitHub milestone."""

    number: int
    title: str
    description: str = ""
    state: str = "open"
    due_on: str | None = None
    open_issues: int = 0
    closed_issues: int = 0


@dataclass(slots=True)
class GitHubRelease:
    """Represents a GitHub release."""

    tag_name: str
    name: str
    body: str = ""
    draft: bool = False
    prerelease: bool = False
    html_url: str = ""
    created_at: str = ""
    published_at: str = ""


@dataclass(slots=True)
class GitHubWorkflowRun:
    """Represents a GitHub Actions workflow run."""

    id: int
    name: str
    status: str = "queued"
    conclusion: str | None = None
    workflow_id: int = 0
    head_branch: str = "main"
    html_url: str = ""
    created_at: str = ""
