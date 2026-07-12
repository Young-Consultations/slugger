"""Project domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Platform(str, Enum):
    """Target output platform for a generated application."""

    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class CodingAgent(str, Enum):
    """Coding agent (AI provider) used for code generation."""

    CODEX = "codex"
    ANTHROPIC = "anthropic"


class AppType(str, Enum):
    """Type of application being built."""

    CLI = "cli"
    WEB = "web"
    API = "api"
    MOBILE = "mobile"


class DesignPreference(str, Enum):
    """Design tooling preference for the project."""

    NONE = "none"
    CANVA = "canva"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ProjectBrief:
    """Typed, immutable project brief that is the authoritative root input for every workflow step.

    This is the single source of truth for what the user wants to build. Every agent
    receives the brief through the execution context so the original idea is never lost.
    """

    idea: str
    platform: Platform
    app_type: AppType = AppType.CLI
    target_users: str = ""
    constraints: list[str] = field(default_factory=list)
    nonfunctional_requirements: list[str] = field(default_factory=list)
    coding_agent: CodingAgent = CodingAgent.CODEX
    design_preference: DesignPreference = DesignPreference.NONE

    def as_metadata(self) -> dict[str, str]:
        """Return a plain-string dict suitable for workflow metadata."""

        return {
            "idea": self.idea,
            "platform": self.platform.value,
            "app_type": self.app_type.value,
            "target_users": self.target_users,
            "constraints": ",".join(self.constraints),
            "nonfunctional_requirements": ",".join(self.nonfunctional_requirements),
            "coding_agent": self.coding_agent.value,
            "design_preference": self.design_preference.value,
        }

    @classmethod
    def from_metadata(cls, metadata: dict[str, str]) -> ProjectBrief:
        """Reconstruct a brief from workflow metadata (supports resume/migration)."""

        idea = metadata.get("idea", "")
        platform_raw = metadata.get("platform", Platform.WEB.value)
        try:
            platform = Platform(platform_raw)
        except ValueError:
            platform = Platform.WEB
        app_type_raw = metadata.get("app_type", AppType.CLI.value)
        try:
            app_type = AppType(app_type_raw)
        except ValueError:
            app_type = AppType.CLI
        coding_agent_raw = metadata.get("coding_agent", CodingAgent.CODEX.value)
        try:
            coding_agent = CodingAgent(coding_agent_raw)
        except ValueError:
            coding_agent = CodingAgent.CODEX
        design_raw = metadata.get("design_preference", DesignPreference.NONE.value)
        try:
            design_preference = DesignPreference(design_raw)
        except ValueError:
            design_preference = DesignPreference.NONE
        constraints_raw = metadata.get("constraints", "")
        constraints = [c for c in constraints_raw.split(",") if c]
        nfr_raw = metadata.get("nonfunctional_requirements", "")
        nonfunctional_requirements = [n for n in nfr_raw.split(",") if n]
        return cls(
            idea=idea,
            platform=platform,
            app_type=app_type,
            target_users=metadata.get("target_users", ""),
            constraints=constraints,
            nonfunctional_requirements=nonfunctional_requirements,
            coding_agent=coding_agent,
            design_preference=design_preference,
        )


@dataclass(slots=True)
class ProjectInput:
    """Structured input supplied by the user to initiate a build.

    Kept for backward compatibility. Use :class:`ProjectBrief` for new code.
    """

    idea: str
    platform: Platform
    coding_agent: CodingAgent = CodingAgent.CODEX

    def as_metadata(self) -> dict[str, str]:
        """Return a plain-string dict suitable for workflow metadata."""

        return {
            "idea": self.idea,
            "platform": self.platform.value,
            "coding_agent": self.coding_agent.value,
        }

    def to_brief(self) -> ProjectBrief:
        """Upgrade to the richer :class:`ProjectBrief` representation."""

        return ProjectBrief(
            idea=self.idea,
            platform=self.platform,
            coding_agent=self.coding_agent,
        )


class ProjectStatus(str, Enum):
    """High-level project status."""

    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectPhase(str, Enum):
    """Lifecycle phase tracked by the AI-SDLC."""

    IDEA = "idea"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    REFLECTION = "reflection"


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
