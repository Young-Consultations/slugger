"""Tests for TASK-043: Artifact Versioning."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from models.artifact import ArtifactMetadata, DocumentArtifact
from models.artifact_version import ArtifactVersionStore, _bump_version
from models.artifact_store_sqlite import SQLiteArtifactStore


def _make_artifact(name: str, content: str = "hello") -> DocumentArtifact:
    return DocumentArtifact(
        artifact_id=str(uuid4()),
        name=name,
        content=content,
        metadata=ArtifactMetadata(source_agent="test", source_step="test"),
    )


def test_bump_version_basic() -> None:
    assert _bump_version("1.0.0") == "1.0.1"
    assert _bump_version("2.3.9") == "2.3.10"
    assert _bump_version("0.0.0") == "0.0.1"


def test_store_first_version() -> None:
    store = ArtifactVersionStore()
    artifact = _make_artifact("spec")
    version = store.store(artifact)
    assert version == "1.0.0"
    assert store.latest("spec") is not None
    assert store.latest("spec").version == "1.0.0"


def test_store_increments_version() -> None:
    store = ArtifactVersionStore()
    a1 = _make_artifact("spec", "v1")
    a2 = _make_artifact("spec", "v2")
    store.store(a1)
    store.store(a2)
    assert store.latest("spec").version == "1.0.1"
    history = store.history("spec")
    assert len(history) == 2
    assert history[0].version == "1.0.0"
    assert history[1].version == "1.0.1"


def test_get_version_by_string() -> None:
    store = ArtifactVersionStore()
    a = _make_artifact("doc")
    store.store(a)
    entry = store.get_version("doc", "1.0.0")
    assert entry is not None
    assert entry.content == "hello"


def test_history_empty_for_unknown() -> None:
    store = ArtifactVersionStore()
    assert store.history("nonexistent") == []
    assert store.latest("nonexistent") is None


def test_multiple_artifacts_are_independent() -> None:
    store = ArtifactVersionStore()
    store.store(_make_artifact("a"))
    store.store(_make_artifact("a"))
    store.store(_make_artifact("b"))
    assert len(store.history("a")) == 2
    assert len(store.history("b")) == 1


def test_sqlite_artifact_store_survives_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "artifacts.db"
    store = SQLiteArtifactStore(db_path)
    artifact = _make_artifact("spec", "restart-safe")
    store.create(artifact)
    reopened = SQLiteArtifactStore(db_path)
    restored = reopened.get(artifact.artifact_id)
    assert restored is not None
    assert restored.content == "restart-safe"
    assert reopened.schema_version() == 1


def test_sqlite_artifact_store_idempotent_under_concurrent_writes(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "artifacts.db"
    store = SQLiteArtifactStore(db_path)
    artifact = _make_artifact("spec", "same-content")

    def _write() -> None:
        store.create(artifact)

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda _: _write(), range(8)))

    history = store.history(artifact.artifact_id)
    assert len(history) == 1
