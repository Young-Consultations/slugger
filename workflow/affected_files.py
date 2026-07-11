"""Affected-files tracker — records which files were produced or modified by each workflow step.

:class:`AffectedFilesTracker` collects file-path entries as steps complete and
provides queries for per-step or per-run impacted paths.  The data is useful
for targeted test selection, incremental builds, and rollback scoping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FileChangeKind(str, Enum):
    """Nature of the file change."""

    CREATED = 'created'
    MODIFIED = 'modified'
    DELETED = 'deleted'


@dataclass
class FileChange:
    """A single file-change record.

    Parameters
    ----------
    path:
        Relative (or absolute) path of the affected file.
    kind:
        How the file was changed.
    step_name:
        The workflow step that produced this change.
    artifact_name:
        Optional: the artifact whose content was written to *path*.
    """

    path: str
    kind: FileChangeKind
    step_name: str
    artifact_name: str = ''


class AffectedFilesTracker:
    """Accumulate and query file changes across workflow steps.

    Examples
    --------
    >>> tracker = AffectedFilesTracker()
    >>> tracker.record('src/main.py', FileChangeKind.CREATED, 'code_generation')
    >>> tracker.for_step('code_generation')
    [FileChange(path='src/main.py', ...)]
    >>> tracker.all_paths()
    ['src/main.py']
    """

    def __init__(self) -> None:
        self._changes: list[FileChange] = []

    # ------------------------------------------------------------------
    # Write API
    # ------------------------------------------------------------------

    def record(
        self,
        path: str | Path,
        kind: FileChangeKind,
        step_name: str,
        artifact_name: str = '',
    ) -> FileChange:
        """Record a file change and return the created :class:`FileChange`.

        Parameters
        ----------
        path:
            The file path affected.
        kind:
            The nature of the change.
        step_name:
            Name of the workflow step that triggered the change.
        artifact_name:
            Optional artifact name associated with the change.
        """
        change = FileChange(
            path=str(path),
            kind=kind,
            step_name=step_name,
            artifact_name=artifact_name,
        )
        self._changes.append(change)
        return change

    def record_artifact_output(
        self,
        artifact_name: str,
        path: str | Path,
        step_name: str,
        kind: FileChangeKind = FileChangeKind.CREATED,
    ) -> FileChange:
        """Convenience method — record a file written from an artifact."""
        return self.record(path, kind, step_name, artifact_name=artifact_name)

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def all_changes(self) -> list[FileChange]:
        """Return all recorded file changes."""
        return list(self._changes)

    def all_paths(self) -> list[str]:
        """Return unique paths of all affected files (insertion order, deduped)."""
        seen: set[str] = set()
        result: list[str] = []
        for change in self._changes:
            if change.path not in seen:
                seen.add(change.path)
                result.append(change.path)
        return result

    def for_step(self, step_name: str) -> list[FileChange]:
        """Return all changes recorded for *step_name*."""
        return [c for c in self._changes if c.step_name == step_name]

    def for_kind(self, kind: FileChangeKind) -> list[FileChange]:
        """Return all changes of the given *kind*."""
        return [c for c in self._changes if c.kind == kind]

    def reset(self) -> None:
        """Clear all recorded changes."""
        self._changes.clear()
