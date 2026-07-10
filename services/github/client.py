"""GitHub REST API client."""

from __future__ import annotations

import os

import requests

from services.github.base import IGitHubService
from services.github.models import GitHubComment, GitHubIssue, GitHubPR, GitHubRepo

_GITHUB_API_BASE = 'https://api.github.com'


class GitHubClient(IGitHubService):
    """GitHub service backed by the GitHub REST API."""

    def __init__(self, owner: str, repo: str, token: str | None = None) -> None:
        self.owner = owner
        self.repo = repo
        self._token = token or os.getenv('GITHUB_TOKEN')
        self._base = _GITHUB_API_BASE

    def _headers(self) -> dict[str, str]:
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
        if self._token:
            headers['Authorization'] = 'Bearer ' + self._token
        return headers

    def _url(self, path: str) -> str:
        return f'{self._base}/repos/{self.owner}/{self.repo}{path}'

    def get_repo(self) -> GitHubRepo:
        response = requests.get(self._url(''), headers=self._headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        return GitHubRepo(
            owner=self.owner,
            name=self.repo,
            default_branch=data.get('default_branch', 'main'),
        )

    def list_issues(self) -> list[GitHubIssue]:
        response = requests.get(
            self._url('/issues'),
            headers=self._headers(),
            params={'state': 'open', 'per_page': 100},
            timeout=30,
        )
        response.raise_for_status()
        return [
            GitHubIssue(
                number=item['number'],
                title=item['title'],
                body=item.get('body') or '',
                state=item['state'],
                labels=[label['name'] for label in item.get('labels', [])],
            )
            for item in response.json()
            if 'pull_request' not in item
        ]

    def list_pull_requests(self) -> list[GitHubPR]:
        response = requests.get(
            self._url('/pulls'),
            headers=self._headers(),
            params={'state': 'open', 'per_page': 100},
            timeout=30,
        )
        response.raise_for_status()
        return [
            GitHubPR(
                number=item['number'],
                title=item['title'],
                body=item.get('body') or '',
                state=item['state'],
            )
            for item in response.json()
        ]

    def create_comment(self, issue_number: int, comment: GitHubComment) -> GitHubComment:
        response = requests.post(
            self._url(f'/issues/{issue_number}/comments'),
            json={'body': comment.body},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return GitHubComment(
            author=data.get('user', {}).get('login', comment.author),
            body=data.get('body', comment.body),
        )
