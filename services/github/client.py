"""GitHub REST API client."""

from __future__ import annotations

import os

import requests

from services.github.base import IGitHubService
from services.github.models import (
    GitHubComment,
    GitHubIssue,
    GitHubMilestone,
    GitHubPR,
    GitHubRelease,
    GitHubRepo,
    GitHubWorkflowRun,
)

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
                milestone_number=(item.get('milestone') or {}).get('number'),
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
                head=item.get('head', {}).get('ref', ''),
                base=item.get('base', {}).get('ref', 'main'),
                milestone_number=(item.get('milestone') or {}).get('number'),
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

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
        milestone_number: int | None = None,
    ) -> GitHubIssue:
        payload: dict[str, object] = {'title': title, 'body': body}
        if labels:
            payload['labels'] = labels
        if milestone_number is not None:
            payload['milestone'] = milestone_number
        response = requests.post(
            self._url('/issues'),
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return GitHubIssue(
            number=data['number'],
            title=data['title'],
            body=data.get('body') or '',
            state=data['state'],
            labels=[label['name'] for label in data.get('labels', [])],
            milestone_number=(data.get('milestone') or {}).get('number'),
        )

    def create_pull_request(self, title: str, body: str, head: str, base: str = 'main') -> GitHubPR:
        response = requests.post(
            self._url('/pulls'),
            json={'title': title, 'body': body, 'head': head, 'base': base},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return GitHubPR(
            number=data['number'],
            title=data['title'],
            body=data.get('body') or '',
            state=data['state'],
            head=data.get('head', {}).get('ref', head),
            base=data.get('base', {}).get('ref', base),
        )

    def list_milestones(self) -> list[GitHubMilestone]:
        response = requests.get(
            self._url('/milestones'),
            headers=self._headers(),
            params={'state': 'open', 'per_page': 100},
            timeout=30,
        )
        response.raise_for_status()
        return [
            GitHubMilestone(
                number=item['number'],
                title=item['title'],
                description=item.get('description') or '',
                state=item['state'],
                due_on=item.get('due_on'),
                open_issues=item.get('open_issues', 0),
                closed_issues=item.get('closed_issues', 0),
            )
            for item in response.json()
        ]

    def create_milestone(self, title: str, description: str = '', due_on: str | None = None) -> GitHubMilestone:
        payload: dict[str, object] = {'title': title, 'description': description}
        if due_on:
            payload['due_on'] = due_on
        response = requests.post(
            self._url('/milestones'),
            json=payload,
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return GitHubMilestone(
            number=data['number'],
            title=data['title'],
            description=data.get('description') or '',
            state=data['state'],
            due_on=data.get('due_on'),
            open_issues=data.get('open_issues', 0),
            closed_issues=data.get('closed_issues', 0),
        )

    def list_releases(self) -> list[GitHubRelease]:
        response = requests.get(
            self._url('/releases'),
            headers=self._headers(),
            params={'per_page': 30},
            timeout=30,
        )
        response.raise_for_status()
        return [
            GitHubRelease(
                tag_name=item['tag_name'],
                name=item.get('name') or '',
                body=item.get('body') or '',
                draft=item.get('draft', False),
                prerelease=item.get('prerelease', False),
                html_url=item.get('html_url', ''),
                created_at=item.get('created_at', ''),
                published_at=item.get('published_at', ''),
            )
            for item in response.json()
        ]

    def create_release(
        self,
        tag_name: str,
        name: str,
        body: str = '',
        draft: bool = False,
        prerelease: bool = False,
    ) -> GitHubRelease:
        response = requests.post(
            self._url('/releases'),
            json={
                'tag_name': tag_name,
                'name': name,
                'body': body,
                'draft': draft,
                'prerelease': prerelease,
            },
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return GitHubRelease(
            tag_name=data['tag_name'],
            name=data.get('name') or '',
            body=data.get('body') or '',
            draft=data.get('draft', False),
            prerelease=data.get('prerelease', False),
            html_url=data.get('html_url', ''),
            created_at=data.get('created_at', ''),
            published_at=data.get('published_at', ''),
        )

    def list_workflow_runs(self, workflow_id: str | int | None = None) -> list[GitHubWorkflowRun]:
        if workflow_id is not None:
            path = f'/actions/workflows/{workflow_id}/runs'
        else:
            path = '/actions/runs'
        response = requests.get(
            self._url(path),
            headers=self._headers(),
            params={'per_page': 30},
            timeout=30,
        )
        response.raise_for_status()
        items = response.json().get('workflow_runs', [])
        return [
            GitHubWorkflowRun(
                id=item['id'],
                name=item.get('name') or '',
                status=item.get('status', 'queued'),
                conclusion=item.get('conclusion'),
                workflow_id=item.get('workflow_id', 0),
                head_branch=item.get('head_branch', ''),
                html_url=item.get('html_url', ''),
                created_at=item.get('created_at', ''),
            )
            for item in items
        ]

    def trigger_workflow(self, workflow_id: str, ref: str = 'main', inputs: dict[str, str] | None = None) -> None:
        response = requests.post(
            self._url(f'/actions/workflows/{workflow_id}/dispatches'),
            json={'ref': ref, 'inputs': inputs or {}},
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
