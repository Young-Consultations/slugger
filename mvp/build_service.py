"""Build-service contract for the narrow Slugger MVP execution path."""

from __future__ import annotations

from typing import Protocol

from mvp.models import MvpBuildResult, MvpProjectRequest


class MvpBuildService(Protocol):
    """Application service interface for one MVP idea-to-PR build."""

    def build(self, request: MvpProjectRequest) -> MvpBuildResult:
        """Build a generated project for the supplied MVP request."""
