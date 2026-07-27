from __future__ import annotations

from copy import deepcopy

import pytest

from orchestrator.contract_orchestration import ContractError, ContractOrchestrator, JsonStateStore


VERSION = "1.0.0"
REQUIRED = {
    "execution_input": {"contract_version", "execution_id", "correlation_id", "source_issue", "executor", "target_repository", "dependencies", "draft_only", "instructions"},
    "execution_result": {"contract_version", "execution_id", "correlation_id", "source_issue", "status", "summary"},
    "task": {"contract_version", "task_id", "correlation_id", "source_issue", "executor", "target_repository", "dependencies", "draft_only", "instructions"},
}


def validator(kind, payload):
    missing = REQUIRED[kind] - payload.keys()
    if missing:
        raise ContractError(f"invalid canonical {kind}: {sorted(missing)}")


@pytest.fixture
def canonical_input():
    return {
        "contract_version": VERSION,
        "execution_id": "exec-1",
        "correlation_id": "corr-9",
        "source_issue": {"repository": "Young-Consultations/portfolio-tasks", "number": 42, "url": "https://example.test/issues/42"},
        "approval_status": "approved",
        "executor": "codex",
        "priority": "p1",
        "task_type": "implementation",
        "target_repository": "Young-Consultations/slugger",
        "dependencies": [],
        "draft_only": True,
        "instructions": "Make the change",
    }


@pytest.fixture
def harness(tmp_path):
    executed, posted = [], []

    def execute(value):
        executed.append(deepcopy(value))
        return {
            "contract_version": VERSION,
            "execution_id": value["execution_id"],
            "correlation_id": value["correlation_id"],
            "source_issue": value["source_issue"],
            "status": "succeeded",
            "summary": "done",
            "artifacts": [],
        }

    service = ContractOrchestrator(
        contract_version=VERSION,
        validator=validator,
        registered_repositories={"Young-Consultations/slugger"},
        state_store=JsonStateStore(tmp_path),
        execute=execute,
        is_success=lambda result: result["status"] == "succeeded",
        post_result=lambda issue, result: posted.append((deepcopy(issue), deepcopy(result))),
    )
    return service, executed, posted


def test_valid_input_and_single_step_produce_final_canonical_result(harness, canonical_input):
    service, executed, posted = harness
    result = service.run(canonical_input).to_dict()
    assert len(executed) == 1
    assert result["status"] == "succeeded"
    assert result["execution_id"] == "exec-1"
    assert result["correlation_id"] == "corr-9"
    assert result["source_issue"] == canonical_input["source_issue"]
    assert posted == [(canonical_input["source_issue"], result)]
    validator("execution_result", result)


def test_invalid_version_is_rejected_before_execution(harness, canonical_input):
    canonical_input["contract_version"] = "99.0.0"
    with pytest.raises(ContractError, match="contract_version"):
        harness[0].run(canonical_input)
    assert harness[1] == []


def test_children_are_canonical_and_propagate_identity(harness, canonical_input):
    service, executed, _ = harness
    service.run(canonical_input, steps=["plan", "implement"])
    assert len(executed) == 2
    for child in executed:
        validator("execution_input", child)
        assert child["correlation_id"] == "corr-9"
        assert child["source_issue"] == canonical_input["source_issue"]
        assert child["parent_execution_id"] == "exec-1"
    assert [item["instructions"] for item in executed] == ["plan", "implement"]
    assert executed[0]["execution_id"] != executed[1]["execution_id"]


def test_child_failure_is_aggregated_and_stops_sequence(harness, canonical_input):
    service, executed, _ = harness

    def fail(value):
        executed.append(value)
        return {"contract_version": VERSION, "execution_id": value["execution_id"], "correlation_id": value["correlation_id"], "source_issue": value["source_issue"], "status": "failed", "summary": "no", "failure_category": "execution"}

    service.execute = fail
    result = service.run(canonical_input, steps=["first", "never"]).to_dict()
    assert result["status"] == "failed"
    assert result["failure_category"] == "execution"
    assert len(executed) == 1


def test_resume_does_not_duplicate_completed_children_or_post(harness, canonical_input):
    service, executed, posted = harness
    first = service.run(canonical_input, steps=["one", "two"]).to_dict()
    second = service.run(canonical_input, steps=["one", "two"]).to_dict()
    assert second == first
    assert len(executed) == 2
    assert len(posted) == 1


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"target_repository": "Young-Consultations/unknown"}, "not registered"),
        ({"dependencies": ["task-2"]}, "unresolved"),
        ({"executor": "human"}, "not Codex"),
        ({"draft_only": False}, "draft_only"),
    ],
)
def test_execution_gates_fail_closed(harness, canonical_input, change, message):
    canonical_input.update(change)
    with pytest.raises(ContractError, match=message):
        harness[0].run(canonical_input)


def test_task_ingestion_uses_same_execution_path(harness, canonical_input):
    task = deepcopy(canonical_input)
    task["task_id"] = task.pop("execution_id")
    result = harness[0].run(task, kind="task")
    assert result.payload["execution_id"] == "exec-1"


def test_legacy_input_has_one_deprecated_migration(harness):
    legacy = {
        "idea": "Build it", "project_name": "demo", "github_repository": "Young-Consultations/slugger",
        "request_identity": "old-1", "source_issue_number": 8, "source_issue_url": "https://example.test/8",
    }
    with pytest.deprecated_call(match="legacy fields"):
        result = harness[0].run(legacy)
    assert result.payload["execution_id"] == "old-1"
    assert harness[1][0]["target_repository"] == "Young-Consultations/slugger"


def test_no_alternate_external_vocabulary(harness, canonical_input):
    result = harness[0].run(canonical_input).to_dict()
    forbidden = {"run_status", "github_repository", "agent", "error_type", "slugger_correlation_id"}
    assert forbidden.isdisjoint(result)
    assert forbidden.isdisjoint(harness[1][0])
