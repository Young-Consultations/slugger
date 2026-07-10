"""Project domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Platform(str, Enum):
    """Target output platform for a generated application."""

    IOS = 'ios'
    ANDROID = 'android'
    WEB = 'web'


class CodingAgent(str, Enum):
    """Coding agent (AI provider) used for code generation."""

    CODEX = 'codex'
    ANTHROPIC = 'anthropic'


@dataclass(slots=True)
class ProjectInput:
    """Structured input supplied by the user to initiate a build."""

    idea: str
    platform: Platform
    coding_agent: CodingAgent = CodingAgent.CODEX

    def as_metadata(self) -> dict[str, str]:
        """Return a plain-string dict suitable for workflow metadata."""

        return {
            'idea': self.idea,
            'platform': self.platform.value,
            'coding_agent': self.coding_agent.value,
        }


class ProjectStatus(str, Enum):
    """High-level project status."""

    DRAFT = 'draft'
    ACTIVE = 'active'
    BLOCKED = 'blocked'
    COMPLETED = 'completed'
    ARCHIVED = 'archived'


class ProjectPhase(str, Enum):
    """Lifecycle phase tracked by the AI-SDLC."""

    IDEA = 'idea'
    REQUIREMENTS = 'requirements'
    ARCHITECTURE = 'architecture'
    PLANNING = 'planning'
    IMPLEMENTATION = 'implementation'
    TESTING = 'testing'
    DEPLOYMENT = 'deployment'
    REFLECTION = 'reflection'


@dataclass(slots=True)
class Project:
    """Represents a software initiative orchestrated by Slugger."""

    project_id: str
    name: str
    description: str
    status: ProjectStatus = ProjectStatus.DRAFT
    phase: ProjectPhase = ProjectPhase.IDEA
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def touch(self) -> None:
        """Update the modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)
