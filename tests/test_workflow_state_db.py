"""Tests for TASK-044: Workflow State Database."""

from __future__ import annotations


from workflow.state_db import WorkflowStateDB
from workflow.models import (
    WorkflowDefinition,
    WorkflowStepDefinition,
    WorkflowInstance,
    StepInstance,
)


def _make_instance(run_id: str = "run-1", status: str = "pending") -> WorkflowInstance:
    step = WorkflowStepDefinition(name="step1", agent="agent1")
    definition = WorkflowDefinition(name="test-workflow", version="1.0.0", steps=[step])
    return WorkflowInstance(
        definition=definition,
        step_instances=[StepInstance(definition=step)],
        status=status,
        run_id=run_id,
    )


def test_save_and_load() -> None:
    db = WorkflowStateDB(":memory:")
    instance = _make_instance("r1", "running")
    db.save(instance)
    loaded = db.load("r1")
    assert loaded is not None
    assert loaded.run_id == "r1"
    assert loaded.status == "running"


def test_load_unknown_returns_none() -> None:
    db = WorkflowStateDB(":memory:")
    assert db.load("no-such-run") is None


def test_list_runs() -> None:
    db = WorkflowStateDB(":memory:")
    db.save(_make_instance("r1"))
    db.save(_make_instance("r2"))
    runs = db.list_runs()
    assert set(runs) == {"r1", "r2"}


def test_list_runs_filtered_by_status() -> None:
    db = WorkflowStateDB(":memory:")
    db.save(_make_instance("r1", "running"))
    db.save(_make_instance("r2", "succeeded"))
    assert db.list_runs(status="running") == ["r1"]
    assert db.list_runs(status="succeeded") == ["r2"]


def test_upsert_updates_status() -> None:
    db = WorkflowStateDB(":memory:")
    instance = _make_instance("r1", "running")
    db.save(instance)
    instance.status = "succeeded"
    db.save(instance)
    loaded = db.load("r1")
    assert loaded.status == "succeeded"


def test_delete() -> None:
    db = WorkflowStateDB(":memory:")
    db.save(_make_instance("r1"))
    db.delete("r1")
    assert db.load("r1") is None
    assert db.list_runs() == []


def test_persistent_db(tmp_path) -> None:
    db_file = tmp_path / "state.db"
    db = WorkflowStateDB(db_file)
    db.save(_make_instance("r1", "succeeded"))
    # Re-open
    db2 = WorkflowStateDB(db_file)
    assert db2.load("r1").status == "succeeded"
