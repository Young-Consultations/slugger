"""Workspace file materializer package (CC-008)."""

from materializer.workspace import (
    WorkspaceState,
    WorkspaceRecord,
    MaterializationResult,
    ProjectMaterializer,
)

__all__ = [
    'MaterializationResult',
    'ProjectMaterializer',
    'WorkspaceRecord',
    'WorkspaceState',
]
