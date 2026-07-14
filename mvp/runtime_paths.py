"""Runtime-home resolution for the focused Slugger MVP path."""

from __future__ import annotations

import os
from pathlib import Path
import stat
import sys


class RuntimePathError(ValueError):
    """Raised when MVP runtime paths are unsafe or cannot be prepared."""


def runtime_home() -> Path:
    """Resolve Slugger's runtime home without using the repository or site-packages.

    Resolution order:
    1. ``SLUGGER_HOME`` when set.
    2. Platform-appropriate per-user data directory.
    3. Development fallback ``~/.slugger`` when platform detection has no home.
    """

    override = os.environ.get("SLUGGER_HOME")
    if override:
        return _prepare_runtime_home(Path(override), source="SLUGGER_HOME")
    return _prepare_runtime_home(_platform_user_data_dir(), source="user data directory")


def workspace_root(home: Path | None = None) -> Path:
    return _prepare_dir((home or runtime_home()) / "workspaces")


def state_dir(home: Path | None = None) -> Path:
    return _prepare_dir((home or runtime_home()) / "state")


def logs_dir(home: Path | None = None) -> Path:
    return _prepare_dir((home or runtime_home()) / "logs")


def sqlite_path(home: Path | None = None) -> Path:
    path = (state_dir(home) / "mvp_runs.sqlite3").resolve(strict=False)
    _validate_runtime_path(path)
    return path


def diagnostics(home: Path | None = None) -> dict[str, str]:
    resolved_home = home or runtime_home()
    return {
        "runtime_home": str(resolved_home),
        "workspace_root": str(workspace_root(resolved_home)),
        "sqlite_path": str(sqlite_path(resolved_home)),
        "logs_dir": str(logs_dir(resolved_home)),
    }


def _platform_user_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / "Slugger"
    elif sys.platform == "darwin":
        home = Path.home()
        if str(home) != ".":
            return home / "Library" / "Application Support" / "Slugger"
    else:
        base = os.environ.get("XDG_DATA_HOME")
        if base:
            return Path(base) / "slugger"
        home = Path.home()
        if str(home) != ".":
            return home / ".local" / "share" / "slugger"
    return Path.home() / ".slugger"


def _prepare_runtime_home(path: Path, *, source: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if resolved == Path(resolved.anchor):
        raise RuntimePathError(f"Refusing to use filesystem root as Slugger runtime home from {source}")
    _validate_runtime_path(resolved)
    return _prepare_dir(resolved)


def _prepare_dir(path: Path) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    _validate_runtime_path(resolved)
    resolved.mkdir(parents=True, exist_ok=True)
    try:
        resolved.chmod(stat.S_IRWXU)
    except OSError:
        pass
    return resolved.resolve(strict=True)


def _validate_runtime_path(path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    try:
        if path.is_relative_to(repo_root):
            raise RuntimePathError("Slugger MVP runtime state must not live inside the source repository")
    except RuntimeError:
        pass
    for parent in (path, *path.parents):
        if parent.name == "site-packages":
            raise RuntimePathError("Slugger MVP runtime state must not live inside site-packages")
