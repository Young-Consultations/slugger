"""GitHub service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.github.models import GitHubComment, GitHubIssue, GitHubPR, GitHubRepo


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
