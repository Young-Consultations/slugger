"""Workspace file materializer package (CC-008)."""

from materializer.build_runner import (
    BuildPhase,
    BuildResult,
    CommandEvidence,
    FakeIsolatedBuildRunner,
    IsolatedBuildRunner,
    PhaseResult,
    PhaseStatus,
)
from materializer.workspace import (
    MaterializationResult,
    ProjectMaterializer,
    WorkspaceRecord,
    WorkspaceState,
)

__all__ = [
    'BuildPhase',
    'BuildResult',
    'CommandEvidence',
    'FakeIsolatedBuildRunner',
    'IsolatedBuildRunner',
    'MaterializationResult',
    'PhaseResult',
    'PhaseStatus',
    'ProjectMaterializer',
    'WorkspaceRecord',
    'WorkspaceState',
]
