"""GitHub client stub."""

from __future__ import annotations

from services.github.base import IGitHubService
from services.github.models import GitHubComment, GitHubIssue, GitHubPR, GitHubRepo


class GitHubClient(IGitHubService):
    def __init__(self, owner: str, repo: str) -> None:
        self.owner = owner
        self.repo = repo

    def get_repo(self) -> GitHubRepo:
        return GitHubRepo(owner=self.owner, name=self.repo)

    def list_issues(self) -> list[GitHubIssue]:
        return []

    def list_pull_requests(self) -> list[GitHubPR]:
        return []

    def create_comment(self, issue_number: int, comment: GitHubComment) -> GitHubComment:
        return comment
