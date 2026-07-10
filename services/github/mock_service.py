"""Mock GitHub service."""

from __future__ import annotations

from services.github.base import IGitHubService
from services.github.models import GitHubComment, GitHubIssue, GitHubPR, GitHubRepo


class MockGitHubService(IGitHubService):
    def __init__(self) -> None:
        self.repo = GitHubRepo(owner='slugger', name='slugger')
        self.issues: list[GitHubIssue] = []
        self.pull_requests: list[GitHubPR] = []
        self.comments: dict[int, list[GitHubComment]] = {}

    def get_repo(self) -> GitHubRepo:
        return self.repo

    def list_issues(self) -> list[GitHubIssue]:
        return list(self.issues)

    def list_pull_requests(self) -> list[GitHubPR]:
        return list(self.pull_requests)

    def create_comment(self, issue_number: int, comment: GitHubComment) -> GitHubComment:
        self.comments.setdefault(issue_number, []).append(comment)
        return comment
