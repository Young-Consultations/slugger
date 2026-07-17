"""Deterministic generated-project manifest creation and verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from pathlib import Path
import shutil
import stat
from typing import Any

MANIFEST_VERSION = 1


class ManifestError(ValueError):
    """Raised when a generated-project manifest is invalid or mismatched."""


class FileType(StrEnum):
    FILE = "file"


@dataclass(frozen=True, order=True)
class ManifestEntry:
    path: str
    sha256: str
    size_bytes: int
    file_type: FileType = FileType.FILE
    executable: bool = False


def create_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    entries: list[ManifestEntry] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        _validate_relative(rel)
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ManifestError(f"Symlink is not allowed: {rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(st.st_mode):
            raise ManifestError(f"Unsupported file type: {rel}")
        data = path.read_bytes()
        entries.append(
            ManifestEntry(
                path=rel,
                sha256=hashlib.sha256(data).hexdigest(),
                size_bytes=len(data),
                executable=bool(st.st_mode & stat.S_IXUSR),
            )
        )
    if not entries:
        raise ManifestError("Generated project is empty")
    json_entries = [entry_to_json(e) for e in sorted(entries)]
    payload: dict[str, Any] = {
        "manifest_version": MANIFEST_VERSION,
        "entries": json_entries,
    }
    payload["artifact_digest"] = manifest_entries_digest(json_entries)
    return payload


def write_manifest(root: Path, output: Path) -> None:
    output.write_text(
        json.dumps(create_manifest(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_protected_manifest(root: Path, output: Path) -> None:
    """Write the canonical protected generated-project manifest."""
    output.write_text(
        json.dumps(create_protected_manifest(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Malformed manifest: {exc}") from exc
    if not isinstance(data, dict) or data.get("manifest_version") != MANIFEST_VERSION:
        raise ManifestError("Unsupported or missing manifest_version")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ManifestError("Manifest entries must be a non-empty list")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ManifestError("Manifest entry must be an object")
        rel = entry.get("path")
        if not isinstance(rel, str):
            raise ManifestError("Manifest entry path must be a string")
        _validate_relative(rel)
        if rel in seen:
            raise ManifestError(f"Duplicate manifest path: {rel}")
        seen.add(rel)
        if entry.get("file_type") != FileType.FILE.value:
            raise ManifestError(f"Unsupported manifest file_type for {rel}")
        if not isinstance(entry.get("sha256"), str) or len(entry["sha256"]) != 64:
            raise ManifestError(f"Invalid sha256 for {rel}")
        if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 0:
            raise ManifestError(f"Invalid size_bytes for {rel}")
        if not isinstance(entry.get("executable"), bool):
            raise ManifestError(f"Invalid executable flag for {rel}")
    if [e["path"] for e in entries] != sorted(e["path"] for e in entries):
        raise ManifestError("Manifest entries must be sorted by path")
    return data


def verify_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    return _verify_manifest_with_factory(root, manifest_path, create_manifest)


def verify_protected_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    """Verify a manifest against the canonical protected-artifact contract."""
    return _verify_manifest_with_factory(root, manifest_path, create_protected_manifest)


def _verify_manifest_with_factory(
    root: Path, manifest_path: Path, factory
) -> dict[str, Any]:
    expected = load_manifest(manifest_path)
    actual = factory(root)
    exp = {e["path"]: e for e in expected["entries"]}
    act = {e["path"]: e for e in actual["entries"]}
    missing = sorted(set(exp) - set(act))
    extra = sorted(set(act) - set(exp))
    mismatched = sorted(path for path in set(exp) & set(act) if exp[path] != act[path])
    if missing or extra or mismatched:
        raise ManifestError(
            f"Manifest mismatch missing={missing} extra={extra} mismatched={mismatched}"
        )
    return {"passed": True, "artifact_digest": expected.get("artifact_digest")}


def manifest_entries_digest(entries: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def entry_to_json(entry: ManifestEntry) -> dict[str, Any]:
    return {
        "path": entry.path,
        "sha256": entry.sha256,
        "size_bytes": entry.size_bytes,
        "file_type": entry.file_type.value,
        "executable": entry.executable,
    }


def _validate_relative(path: str) -> None:
    p = Path(path)
    if (
        not path
        or "\x00" in path
        or p.is_absolute()
        or any(part in {"", ".", ".."} for part in p.parts)
    ):
        raise ManifestError(f"Unsafe manifest path: {path!r}")


_RUNTIME_DIRS = {".venv", "__pycache__", ".pytest_cache", "build", "dist", "htmlcov"}
_RUNTIME_SUFFIXES = {".pyc"}
_RUNTIME_FILES = {".coverage"}
_RUNTIME_SUFFIX_PATTERNS = (".egg-info",)


def create_protected_manifest(root: Path) -> dict[str, Any]:
    """Create a manifest for protected generated source/configuration files only."""
    root = root.resolve(strict=True)
    entries: list[ManifestEntry] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if _is_runtime_artifact(path.relative_to(root)):
            continue
        _validate_relative(rel)
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ManifestError(f"Symlink is not allowed: {rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(st.st_mode):
            raise ManifestError(f"Unsupported file type: {rel}")
        data = path.read_bytes()
        entries.append(
            ManifestEntry(
                path=rel,
                sha256=hashlib.sha256(data).hexdigest(),
                size_bytes=len(data),
                executable=bool(st.st_mode & stat.S_IXUSR),
            )
        )
    if not entries:
        raise ManifestError("Generated project is empty")
    json_entries = [entry_to_json(e) for e in sorted(entries)]
    return {
        "manifest_version": MANIFEST_VERSION,
        "entries": json_entries,
        "artifact_digest": manifest_entries_digest(json_entries),
    }


def _is_runtime_artifact(relative: Path) -> bool:
    parts = relative.parts
    if any(
        part in _RUNTIME_DIRS or part.endswith(_RUNTIME_SUFFIX_PATTERNS)
        for part in parts
    ):
        return True
    return relative.name in _RUNTIME_FILES or relative.suffix in _RUNTIME_SUFFIXES


def sanitize_protected_artifact(raw_root: Path, sanitized_root: Path) -> dict[str, Any]:
    """Copy only protected-manifest files from ``raw_root`` to ``sanitized_root``.

    The raw tree is fully validated for prohibited paths, symlinks, and special
    files. Known runtime/build artifacts are ignored by the protected manifest;
    all protected files are copied with executable bits preserved.
    """
    raw = raw_root.resolve(strict=True)
    destination = sanitized_root.resolve(strict=False)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    _validate_tree_security(raw)
    manifest = create_protected_manifest(raw)
    for entry in manifest["entries"]:
        rel = entry["path"]
        _validate_relative(rel)
        source = (raw / rel).resolve(strict=True)
        if not source.is_relative_to(raw):
            raise ManifestError(f"Protected source escapes root: {rel}")
        st = source.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ManifestError(f"Symlink is not allowed: {rel}")
        if not stat.S_ISREG(st.st_mode):
            raise ManifestError(f"Unsupported file type: {rel}")
        target = (destination / rel).resolve(strict=False)
        if not target.is_relative_to(destination):
            raise ManifestError(f"Sanitized target escapes root: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
        if entry.get("executable"):
            target.chmod(target.stat().st_mode | stat.S_IXUSR)
        else:
            target.chmod(
                target.stat().st_mode & ~stat.S_IXUSR & ~stat.S_IXGRP & ~stat.S_IXOTH
            )
    sanitized_manifest = create_protected_manifest(destination)
    if sanitized_manifest["artifact_digest"] != manifest["artifact_digest"]:
        raise ManifestError("Sanitized artifact digest mismatch")
    return sanitized_manifest


def _validate_tree_security(root: Path) -> None:
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        rel = rel_path.as_posix()
        _validate_relative(rel)
        if any(part in {".git", ".github"} for part in rel_path.parts):
            raise ManifestError(f"Prohibited generated path: {rel}")
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            raise ManifestError(f"Generated path escapes root: {rel}")
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise ManifestError(f"Symlink is not allowed: {rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(st.st_mode):
            raise ManifestError(f"Unsupported file type: {rel}")
