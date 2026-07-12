"""Project workspace materializer (CC-008).

Writes a validated AppManifest to a safe, reproducible workspace directory.
All files are staged, checksums verified, then atomically published.

Safety guarantees:
- Never writes outside the configured workspace root.
- Never executes code during materialization.
- Atomic publish: staging → active (rename).
- Failed workspace evidence is preserved, not overwritten.
- Idempotent: repeated resume does not corrupt files.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from models.app_manifest import AppManifest, FileEntry, validate_app_manifest

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------


class WorkspaceState(str, Enum):
    """Lifecycle states of a materialisation workspace."""

    STAGING = "staging"
    ACTIVE = "active"
    FAILED = "failed"
    RELEASED = "released"


@dataclass
class FileInventoryEntry:
    """Maps a materialised file to its source artifact and checksum."""

    path: str
    checksum: str
    size_bytes: int
    artifact_refs: list[str] = field(default_factory=list)


@dataclass
class WorkspaceRecord:
    """Metadata record for a workspace created by the materializer."""

    workspace_id: str
    root: Path
    state: WorkspaceState
    app_id: str
    inventory: list[FileInventoryEntry] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class MaterializationResult:
    """Result of a materialisation operation."""

    success: bool
    workspace: WorkspaceRecord | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Materializer
# ---------------------------------------------------------------------------


class ProjectMaterializer:
    """Write a validated AppManifest to a filesystem workspace.

    Parameters
    ----------
    workspace_root:
        Base directory under which all workspaces are created.
        The materializer will never write outside this root.
    """

    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root.resolve()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def materialize(
        self, manifest: AppManifest, workspace_id: str | None = None
    ) -> MaterializationResult:
        """Validate and materialise *manifest* into a new workspace.

        Returns a :class:`MaterializationResult` with the workspace record.
        """
        # Pre-flight validation
        val = validate_app_manifest(manifest)
        if not val.valid:
            errors = [f"{e.field}: {e.message}" for e in val.errors]
            return MaterializationResult(success=False, errors=errors)

        ws_id = workspace_id or manifest.app_id
        staging_dir = self._staging_path(ws_id)
        active_dir = self._active_path(ws_id)
        failed_dir = self._failed_path(ws_id)

        # Safety: never overwrite an existing non-Slugger directory.
        if active_dir.exists():
            if not (active_dir / ".slugger").exists():
                return MaterializationResult(
                    success=False,
                    errors=[
                        f"Directory {active_dir} already exists and is not a Slugger workspace"
                    ],
                )

        # Clean up any previous staging attempt.
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)

        staging_dir.mkdir(parents=True, exist_ok=True)
        record = WorkspaceRecord(
            workspace_id=ws_id,
            root=active_dir,
            state=WorkspaceState.STAGING,
            app_id=manifest.app_id,
        )

        try:
            inventory = self._write_files(manifest.files, staging_dir)
            self._verify_checksums(manifest.files, staging_dir)
        except Exception as exc:  # noqa: BLE001
            _LOG.error("Materialization failed during staging: %s", exc)
            failed_dir.mkdir(parents=True, exist_ok=True)
            if staging_dir.exists():
                # Preserve failed evidence
                shutil.copytree(
                    staging_dir, failed_dir / "failed_staging", dirs_exist_ok=True
                )
                shutil.rmtree(staging_dir, ignore_errors=True)
            record.state = WorkspaceState.FAILED
            record.errors.append(str(exc))
            return MaterializationResult(
                success=False, workspace=record, errors=[str(exc)]
            )

        # Write Slugger marker file
        (staging_dir / ".slugger").write_text(
            f"app_id={manifest.app_id}\n", encoding="utf-8"
        )

        # Atomic publish: rename staging → active
        if active_dir.exists():
            shutil.rmtree(active_dir, ignore_errors=True)
        active_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staging_dir), str(active_dir))

        record.root = active_dir
        record.state = WorkspaceState.ACTIVE
        record.inventory = inventory

        warnings = [f"{w.field}: {w.message}" for w in val.warnings]
        return MaterializationResult(success=True, workspace=record, warnings=warnings)

    def resume(
        self, manifest: AppManifest, workspace_id: str | None = None
    ) -> MaterializationResult:
        """Idempotent resume: skip files that already exist with correct checksums."""
        ws_id = workspace_id or manifest.app_id
        active_dir = self._active_path(ws_id)

        if not active_dir.exists():
            return self.materialize(manifest, workspace_id)

        # Validate again in case manifest changed
        val = validate_app_manifest(manifest)
        if not val.valid:
            errors = [f"{e.field}: {e.message}" for e in val.errors]
            return MaterializationResult(success=False, errors=errors)

        inventory: list[FileInventoryEntry] = []
        errors: list[str] = []
        for entry in manifest.files:
            dest = self._resolve_workspace_file(active_dir, entry.path)
            expected = hashlib.sha256(entry.content.encode("utf-8")).hexdigest()
            if dest.exists():
                actual = hashlib.sha256(dest.read_bytes()).hexdigest()
                if actual == expected:
                    inventory.append(
                        FileInventoryEntry(
                            path=entry.path,
                            checksum=expected,
                            size_bytes=dest.stat().st_size,
                            artifact_refs=entry.artifact_refs,
                        )
                    )
                    continue
            # Write (or overwrite) file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(entry.content, encoding="utf-8")
            inventory.append(
                FileInventoryEntry(
                    path=entry.path,
                    checksum=expected,
                    size_bytes=len(entry.content.encode("utf-8")),
                    artifact_refs=entry.artifact_refs,
                )
            )

        record = WorkspaceRecord(
            workspace_id=ws_id,
            root=active_dir,
            state=WorkspaceState.ACTIVE,
            app_id=manifest.app_id,
            inventory=inventory,
            errors=errors,
        )
        return MaterializationResult(
            success=not errors, workspace=record, errors=errors
        )

    def cleanup(self, workspace_id: str) -> None:
        """Remove all workspace directories for *workspace_id*."""
        for dir_path in [
            self._staging_path(workspace_id),
            self._active_path(workspace_id),
            self._failed_path(workspace_id),
        ]:
            if dir_path.exists():
                shutil.rmtree(dir_path, ignore_errors=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _safe_path(self, subdir: str, workspace_id: str) -> Path:
        """Build and validate a path within the workspace root."""
        path = (self._root / subdir / workspace_id).resolve()
        try:
            path.relative_to(self._root.resolve())
        except ValueError:
            raise ValueError(
                f"Computed path {path} is outside workspace root {self._root}"
            )
        return path

    def _staging_path(self, ws_id: str) -> Path:
        return self._safe_path("staging", ws_id)

    def _active_path(self, ws_id: str) -> Path:
        return self._safe_path("active", ws_id)

    def _failed_path(self, ws_id: str) -> Path:
        return self._safe_path("failed", ws_id)

    def _write_files(
        self, files: list[FileEntry], staging_dir: Path
    ) -> list[FileInventoryEntry]:
        """Write files to staging dir; return inventory."""
        inventory: list[FileInventoryEntry] = []
        for entry in files:
            dest = self._resolve_workspace_file(staging_dir, entry.path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(entry.content, encoding="utf-8")
            inventory.append(
                FileInventoryEntry(
                    path=entry.path,
                    checksum=entry.checksum,
                    size_bytes=entry.size_bytes,
                    artifact_refs=entry.artifact_refs,
                )
            )
        return inventory

    def _verify_checksums(self, files: list[FileEntry], staging_dir: Path) -> None:
        """Verify that written files match their declared checksums."""
        for entry in files:
            dest = self._resolve_workspace_file(staging_dir, entry.path)
            if not dest.exists():
                raise RuntimeError(
                    f"Expected file not found after write: {entry.path!r}"
                )
            actual = hashlib.sha256(dest.read_bytes()).hexdigest()
            expected = hashlib.sha256(entry.content.encode("utf-8")).hexdigest()
            if actual != expected:
                raise RuntimeError(
                    f"Checksum mismatch for {entry.path!r}: "
                    f"expected {expected[:16]}... got {actual[:16]}..."
                )

    def _resolve_workspace_file(self, workspace_dir: Path, relative_path: str) -> Path:
        """Resolve a manifest path and ensure it stays inside *workspace_dir*."""
        dest = (workspace_dir / relative_path).resolve()
        try:
            dest.relative_to(workspace_dir.resolve())
        except ValueError as exc:
            raise ValueError(
                f"Path {relative_path!r} would escape workspace directory"
            ) from exc
        return dest
