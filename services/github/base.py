"""GitHub service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.github.models import (
    GitHubComment,
    GitHubIssue,
    GitHubMilestone,
    GitHubPR,
    GitHubRelease,
    GitHubRepo,
    GitHubWorkflowRun,
)


class IGitHubService(ABC):
    @abstractmethod
    def get_repo(self) -> GitHubRepo:
        """Return repository metadata."""

    @abstractmethod
    def list_issues(self) -> list[GitHubIssue]:
        """Return repository issues."""

    @abstractmethod
    def list_pull_requests(self) -> list[GitHubPR]:
        """Return repository pull requests."""

    @abstractmethod
    def create_comment(self, issue_number: int, comment: GitHubComment) -> GitHubComment:
        """Create a comment on an issue or pull request."""

    @abstractmethod
    def create_issue(self, title: str, body: str, labels: list[str] | None = None, milestone_number: int | None = None) -> GitHubIssue:
        """Create a new issue."""

    @abstractmethod
    def create_pull_request(self, title: str, body: str, head: str, base: str = 'main', draft: bool = False) -> GitHubPR:
        """Open a new pull request from *head* into *base*."""

    @abstractmethod
    def list_milestones(self) -> list[GitHubMilestone]:
        """Return open milestones."""

    @abstractmethod
    def create_milestone(self, title: str, description: str = '', due_on: str | None = None) -> GitHubMilestone:
        """Create a new milestone."""

    @abstractmethod
    def list_releases(self) -> list[GitHubRelease]:
        """Return releases."""

    @abstractmethod
    def create_release(self, tag_name: str, name: str, body: str = '', draft: bool = False, prerelease: bool = False) -> GitHubRelease:
        """Create a new release."""

    @abstractmethod
    def list_workflow_runs(self, workflow_id: str | int | None = None) -> list[GitHubWorkflowRun]:
        """Return recent workflow runs."""

    @abstractmethod
    def trigger_workflow(self, workflow_id: str, ref: str = 'main', inputs: dict[str, str] | None = None) -> None:
        """Trigger a workflow dispatch event."""
