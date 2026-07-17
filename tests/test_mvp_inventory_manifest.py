from pathlib import Path
import json
import os

import pytest

from mvp.inventory_manifest import (
    ManifestError,
    create_manifest,
    create_protected_manifest,
    sanitize_protected_artifact,
    verify_manifest,
    verify_protected_manifest,
    write_manifest,
    write_protected_manifest,
)


def test_manifest_order_and_sha(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "a.txt").write_text("a")
    manifest = create_manifest(tmp_path)
    assert [e["path"] for e in manifest["entries"]] == ["a.txt", "b.txt"]
    out = tmp_path.parent / "manifest.json"
    write_manifest(tmp_path, out)
    assert verify_manifest(tmp_path, out)["passed"] is True


def test_manifest_rejects_missing_extra_modified_and_mode(tmp_path: Path) -> None:
    f = tmp_path / "a.sh"
    f.write_text("a")
    manifest = tmp_path.parent / "manifest.json"
    write_manifest(tmp_path, manifest)
    f.write_text("b")
    with pytest.raises(ManifestError):
        verify_manifest(tmp_path, manifest)
    f.write_text("a")
    os.chmod(f, 0o755)
    with pytest.raises(ManifestError):
        verify_manifest(tmp_path, manifest)
    os.chmod(f, 0o644)
    (tmp_path / "extra.txt").write_text("x")
    with pytest.raises(ManifestError):
        verify_manifest(tmp_path, manifest)


def test_manifest_rejects_symlink_malformed_and_traversal(tmp_path: Path) -> None:
    (tmp_path / "target").write_text("x")
    (tmp_path / "link").symlink_to(tmp_path / "target")
    with pytest.raises(ManifestError):
        create_manifest(tmp_path)
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(ManifestError):
        verify_manifest(tmp_path, bad)
    bad.write_text(
        json.dumps(
            {
                "manifest_version": 1,
                "entries": [
                    {
                        "path": "../x",
                        "sha256": "0" * 64,
                        "size_bytes": 1,
                        "file_type": "file",
                        "executable": False,
                    }
                ],
            }
        )
    )
    with pytest.raises(ManifestError):
        verify_manifest(tmp_path, bad)


def _write_hello_artifact(root: Path) -> None:
    (root / "src" / "hello_codex" / "__pycache__").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "README.md").write_text("# hello\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "[project]\nname='hello-codex'\n", encoding="utf-8"
    )
    (root / "src" / "hello_codex" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "hello_codex" / "main.py").write_text(
        "print('Hello, Joseph!')\n", encoding="utf-8"
    )
    (root / "tests" / "test_main.py").write_text(
        "def test_ok(): assert True\n", encoding="utf-8"
    )
    (root / "src" / "hello_codex" / "__pycache__" / "main.cpython-312.pyc").write_bytes(
        b"pyc"
    )
    (
        root / "src" / "hello_codex" / "__pycache__" / "__init__.cpython-312.pyc"
    ).write_bytes(b"pyc")
    (root / ".pytest_cache").mkdir()
    (root / ".pytest_cache" / "README.md").write_text("cache", encoding="utf-8")
    (root / "src" / "hello_codex.egg-info").mkdir()
    (root / "src" / "hello_codex.egg-info" / "PKG-INFO").write_text(
        "cache", encoding="utf-8"
    )
    (root / "build").mkdir()
    (root / "build" / "artifact").write_text("cache", encoding="utf-8")
    (root / "dist").mkdir()
    (root / "dist" / "artifact.whl").write_text("cache", encoding="utf-8")
    (root / ".coverage").write_text("cache", encoding="utf-8")


def test_protected_manifest_and_sanitizer_exclude_runtime_artifacts(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_hello_artifact(raw)

    manifest = create_protected_manifest(raw)
    assert [entry["path"] for entry in manifest["entries"]] == [
        "README.md",
        "pyproject.toml",
        "src/hello_codex/__init__.py",
        "src/hello_codex/main.py",
        "tests/test_main.py",
    ]
    out = tmp_path / "manifest.json"
    write_protected_manifest(raw, out)
    sanitized = tmp_path / "sanitized"
    sanitized_manifest = sanitize_protected_artifact(raw, sanitized)
    assert sanitized_manifest["artifact_digest"] == manifest["artifact_digest"]
    assert sorted(
        p.relative_to(sanitized).as_posix() for p in sanitized.rglob("*") if p.is_file()
    ) == [
        "README.md",
        "pyproject.toml",
        "src/hello_codex/__init__.py",
        "src/hello_codex/main.py",
        "tests/test_main.py",
    ]
    assert verify_protected_manifest(sanitized, out)["passed"] is True


def test_sanitizer_rejects_symlink_even_under_runtime_directory(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    _write_hello_artifact(raw)
    (raw / "src" / "hello_codex" / "__pycache__" / "link.pyc").symlink_to(
        raw / "README.md"
    )
    with pytest.raises(ManifestError):
        sanitize_protected_artifact(raw, tmp_path / "sanitized")
