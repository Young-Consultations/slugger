"""Tests for TASK-046: Affected Files."""

from __future__ import annotations

from workflow.affected_files import AffectedFilesTracker, FileChangeKind


def test_record_and_all_paths() -> None:
    tracker = AffectedFilesTracker()
    tracker.record("src/main.py", FileChangeKind.CREATED, "codegen")
    tracker.record("tests/test_main.py", FileChangeKind.CREATED, "test_gen")
    assert tracker.all_paths() == ["src/main.py", "tests/test_main.py"]


def test_all_paths_deduplicates() -> None:
    tracker = AffectedFilesTracker()
    tracker.record("a.py", FileChangeKind.CREATED, "step1")
    tracker.record("a.py", FileChangeKind.MODIFIED, "step2")
    assert tracker.all_paths() == ["a.py"]


def test_for_step() -> None:
    tracker = AffectedFilesTracker()
    tracker.record("a.py", FileChangeKind.CREATED, "step1")
    tracker.record("b.py", FileChangeKind.MODIFIED, "step2")
    result = tracker.for_step("step1")
    assert len(result) == 1
    assert result[0].path == "a.py"


def test_for_kind() -> None:
    tracker = AffectedFilesTracker()
    tracker.record("a.py", FileChangeKind.CREATED, "step1")
    tracker.record("b.py", FileChangeKind.DELETED, "step2")
    created = tracker.for_kind(FileChangeKind.CREATED)
    assert len(created) == 1
    deleted = tracker.for_kind(FileChangeKind.DELETED)
    assert len(deleted) == 1


def test_record_artifact_output() -> None:
    tracker = AffectedFilesTracker()
    change = tracker.record_artifact_output("source_code", "src/app.py", "code_gen")
    assert change.artifact_name == "source_code"
    assert change.path == "src/app.py"
    assert change.kind == FileChangeKind.CREATED


def test_reset() -> None:
    tracker = AffectedFilesTracker()
    tracker.record("x.py", FileChangeKind.CREATED, "s")
    tracker.reset()
    assert tracker.all_changes() == []
    assert tracker.all_paths() == []
