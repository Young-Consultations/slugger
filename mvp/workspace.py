"""Isolated workspace management for the Slugger MVP path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import uuid

from mvp.models import GeneratedFile, GeneratedProjectInventory


class WorkspaceSafetyError(ValueError):
    """Raised when a workspace path would violate the MVP safety boundary."""


@dataclass(frozen=True)
class MvpWorkspace:
    """A single isolated directory assigned to one MVP run."""

    run_id: str
    path: Path


EXCLUDED_INVENTORY_PARTS = {
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "test-deps",
    "wheelhouse",
    "dist",
    "build",
}
EXCLUDED_INVENTORY_SUFFIXES = (".pyc",)


class WorkspaceManager:
    """Create, validate, inventory, and clean MVP-generated project workspaces."""

    def __init__(
        self, workspace_root: Path | str = Path(".slugger/workspaces")
    ) -> None:
        raw_root = Path(workspace_root).expanduser()
        self.root = raw_root.resolve(strict=False)
        self._reject_repository_root(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.root = self.root.resolve(strict=True)
        self._reject_repository_root(self.root)

    def create_workspace(self, run_id: str | None = None) -> MvpWorkspace:
        """Create a unique workspace below the approved root for a run."""

        normalized_run_id = self._normalize_run_id(run_id or uuid.uuid4().hex)
        for _ in range(10):
            candidate = (self.root / normalized_run_id).resolve(strict=False)
            self._require_below_root(candidate)
            try:
                candidate.mkdir(parents=False, exist_ok=False)
            except FileExistsError:
                normalized_run_id = f"{normalized_run_id}-{uuid.uuid4().hex[:8]}"
                continue
            self._require_below_root(candidate.resolve(strict=True))
            return MvpWorkspace(run_id=normalized_run_id, path=candidate)
        raise WorkspaceSafetyError("Could not create a unique MVP workspace")

    def resolve_generated_path(
        self, workspace: Path | MvpWorkspace, relative_path: str | Path
    ) -> Path:
        """Resolve a generated-project path and reject traversal or root escapes."""

        workspace_path = self._workspace_path(workspace)
        path = Path(relative_path)
        self._validate_relative_path(path)
        resolved = (workspace_path / path).resolve(strict=False)
        self._require_below_workspace(workspace_path, resolved)
        return resolved

    def inventory(self, workspace: Path | MvpWorkspace) -> GeneratedProjectInventory:
        """Return a deterministic inventory for regular files in the workspace."""

        workspace_path = self._workspace_path(workspace)
        files: list[GeneratedFile] = []
        for path in sorted(
            p for p in workspace_path.rglob("*") if p.is_file() or p.is_symlink()
        ):
            relative = path.relative_to(workspace_path)
            self._validate_relative_path(relative)
            if _is_excluded_inventory_path(relative):
                continue
            resolved = path.resolve(strict=True)
            self._require_below_workspace(workspace_path, resolved)
            if not resolved.is_file():
                raise WorkspaceSafetyError(
                    f"Generated path is not a regular file: {relative}"
                )
            data = resolved.read_bytes()
            files.append(
                GeneratedFile(
                    path=relative.as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(),
                    size_bytes=len(data),
                )
            )

        if not files:
            raise WorkspaceSafetyError("Workspace inventory is empty")
        inventory_payload = [file.__dict__ for file in files]
        inventory_hash = hashlib.sha256(
            json.dumps(inventory_payload, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        return GeneratedProjectInventory(
            files=tuple(files), inventory_hash=inventory_hash
        )

    def cleanup(self, workspace: Path | MvpWorkspace) -> None:
        """Explicitly remove a workspace after callers no longer need evidence."""

        workspace_path = self._workspace_path(workspace)
        self._require_below_root(workspace_path)
        shutil.rmtree(workspace_path)

    def _workspace_path(self, workspace: Path | MvpWorkspace) -> Path:
        path = (
            workspace.path if isinstance(workspace, MvpWorkspace) else Path(workspace)
        )
        resolved = path.expanduser().resolve(strict=True)
        self._require_below_root(resolved)
        if resolved == self.root:
            raise WorkspaceSafetyError("Workspace must be a run-specific directory")
        return resolved

    def _require_below_root(self, path: Path) -> None:
        if not path.is_relative_to(self.root):
            raise WorkspaceSafetyError(f"Workspace path escapes approved root: {path}")

    @staticmethod
    def _require_below_workspace(workspace_path: Path, path: Path) -> None:
        if not path.is_relative_to(workspace_path):
            raise WorkspaceSafetyError(f"Generated path escapes workspace: {path}")

    @staticmethod
    def _validate_relative_path(path: Path) -> None:
        text = path.as_posix()
        if "\x00" in text:
            raise WorkspaceSafetyError("Generated path contains a null byte")
        if path.is_absolute():
            raise WorkspaceSafetyError("Generated paths must be workspace-relative")
        if any(part == ".." for part in path.parts):
            raise WorkspaceSafetyError(
                "Generated paths must not contain parent traversal"
            )

    @staticmethod
    def _normalize_run_id(run_id: str) -> str:
        normalized = run_id.strip()
        if not normalized:
            raise WorkspaceSafetyError("run_id is required")
        path = Path(normalized)
        if (
            path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or len(path.parts) != 1
        ):
            raise WorkspaceSafetyError("run_id must be a single safe path segment")
        return normalized

    @staticmethod
    def _reject_repository_root(path: Path) -> None:
        if (path / ".git").exists() and (path / "pyproject.toml").exists():
            raise WorkspaceSafetyError(
                "The Slugger repository root cannot be an MVP workspace root"
            )


def _is_excluded_inventory_path(path: Path) -> bool:
    if any(
        part in EXCLUDED_INVENTORY_PARTS or part.endswith(".egg-info")
        for part in path.parts
    ):
        return True
    return path.name.endswith(EXCLUDED_INVENTORY_SUFFIXES)
