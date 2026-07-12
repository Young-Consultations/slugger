"""Tests for TASK-048: Rollback Guidance."""

from __future__ import annotations

from workflow.rollback import RollbackGuidance, RollbackStep


def test_register_and_retrieve() -> None:
    guidance = RollbackGuidance(run_id="abc")
    step = RollbackStep(
        "deploy", "Delete k8s resources", commands=["kubectl delete -f ."]
    )
    guidance.register(step)
    retrieved = guidance.for_step("deploy")
    assert retrieved is not None
    assert retrieved.description == "Delete k8s resources"
    assert retrieved.commands == ["kubectl delete -f ."]


def test_register_simple() -> None:
    guidance = RollbackGuidance()
    step = guidance.register_simple("test", "Re-run failing tests", ["pytest"])
    assert guidance.for_step("test") is step


def test_all_steps_order() -> None:
    guidance = RollbackGuidance()
    guidance.register_simple("a", "Step A")
    guidance.register_simple("b", "Step B")
    names = [s.step_name for s in guidance.all_steps()]
    assert names == ["a", "b"]


def test_overwrite() -> None:
    guidance = RollbackGuidance()
    guidance.register_simple("deploy", "Old description")
    guidance.register_simple("deploy", "New description")
    assert guidance.for_step("deploy").description == "New description"
    assert len(guidance.all_steps()) == 1


def test_round_trip_dict() -> None:
    guidance = RollbackGuidance(run_id="xyz")
    guidance.register_simple("build", "Rebuild artifacts", ["make build"])
    data = guidance.to_dict()
    restored = RollbackGuidance.from_dict(data)
    assert restored.run_id == "xyz"
    step = restored.for_step("build")
    assert step is not None
    assert step.commands == ["make build"]


def test_unknown_step_returns_none() -> None:
    guidance = RollbackGuidance()
    assert guidance.for_step("nonexistent") is None
