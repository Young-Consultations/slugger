from pathlib import Path
import json
import os

import pytest

from mvp.inventory_manifest import (
    ManifestError,
    create_manifest,
    verify_manifest,
    write_manifest,
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
