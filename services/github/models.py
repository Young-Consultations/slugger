"""GitHub service models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GitHubRepo:
    owner: str
    name: str
    default_branch: str = 'main'


@dataclass(slots=True)
class GitHubIssue:
    number: int
    title: str
    body: str
    state: str = 'open'
    labels: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GitHubPR:
    number: int
    title: str
    body: str
    state: str = 'open'


@dataclass(slots=True)
class GitHubComment:
    author: str
    body: str
