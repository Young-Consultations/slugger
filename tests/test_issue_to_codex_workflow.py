from pathlib import Path

import pytest
import yaml

from mvp.codex_target import (
    TargetPolicyError,
    authorize_slugger_execution,
    deterministic_branch,
)

TARGET_WORKFLOW = Path(".github/workflows/codex-execute.yml")
ISSUE_WORKFLOW = Path(".github/workflows/issue-to-codex.yml")
USER_IDEA_WORKFLOW = Path(".github/workflows/user-idea-codex-cli-demo.yml")
ALLOWLIST = Path(".github/slugger/target-allowlist.json")


def _workflow(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _canonical(**overrides):
    data = {
        "contract_version": "ai-sdlc-contract/v3",
        "contract": "ai-sdlc-contract/v2",
        "delivery_id": "delivery-123",
        "requested_branch": deterministic_branch("delivery-123"),
        "draft_pr_only": True,
        "mode": "verify",
        "correlation_id": "corr-123",
        "target": {"repository": "Young-Consultations/slugger", "executor": "Codex"},
        "source": {
            "repository": "Young-Consultations/portfolio-tasks",
            "issue_number": 123,
            "issue_state": "open",
        },
        "governance": {"approved": True},
        "task": {
            "id": "task-123",
            "type": "mvp_python_cli",
            "sensitive": False,
            "idea": "Build a tiny calculator CLI.",
            "project_name": "calculator-demo",
        },
        "publication": {"mode": "draft_pr", "identity": "delivery-123"},
    }
    for key, value in overrides.items():
        data[key] = value
    return data


def test_production_target_workflow_exists_and_accepts_router_inputs() -> None:
    data = _workflow(TARGET_WORKFLOW)
    dispatch = data[True]["workflow_dispatch"]["inputs"]
    assert set(dispatch) == {
        "execution_input_json",
        "execution_input_artifact",
        "execution_input_run_id",
        "concurrency_group",
    }
    assert dispatch["concurrency_group"]["required"] is True
    assert dispatch["execution_input_json"]["type"] == "string"
    assert dispatch["execution_input_artifact"]["type"] == "string"
    assert dispatch["execution_input_run_id"]["type"] == "string"


def test_target_workflow_uses_router_concurrency_and_no_issue_triggers() -> None:
    data = _workflow(TARGET_WORKFLOW)
    assert data["concurrency"] == {
        "group": "${{ inputs.concurrency_group }}",
        "cancel-in-progress": False,
    }
    assert set(data[True]) == {"workflow_dispatch"}
    assert "issues" not in data[True]
    assert "issue_comment" not in data[True]
    assert "pull_request_target" not in data[True]
    assert "repository_dispatch" not in data[True]


def test_target_workflow_installs_pinned_organization_contracts() -> None:
    text = TARGET_WORKFLOW.read_text(encoding="utf-8")
    assert "repository: Young-Consultations/.github" in text
    assert "ref: ai-sdlc-v2.1.0" in text
    assert "path: .ai-sdlc-control-plane" in text
    assert "persist-credentials: false" in text
    assert 'python -m pip install -e "./.ai-sdlc-control-plane"' in text
    assert "validate_execution_input" in text
    assert "validate_execution_result" in text


def test_slugger_does_not_locally_define_canonical_contract_or_old_bridge() -> None:
    assert not ISSUE_WORKFLOW.exists()
    assert not ALLOWLIST.exists()
    assert not Path("mvp/issue_bridge.py").exists()
    text = TARGET_WORKFLOW.read_text(encoding="utf-8")
    assert "portfolio-task-source" not in text
    assert "AUTHORIZED_CODEX_READY_ACTORS" not in text
    assert "request_identity" not in text


def test_no_issue_event_or_codex_ready_can_start_production_codex() -> None:
    workflows = list(Path(".github/workflows").glob("*.yml")) + list(
        Path(".github/workflows").glob("*.yaml")
    )
    for workflow in workflows:
        data = _workflow(workflow)
        text = workflow.read_text(encoding="utf-8")
        if "openai/codex-action" in text or "user-idea-codex-cli-demo.yml" in text:
            assert "issues" not in data.get(True, {})
            assert "codex-ready" not in text


def test_no_production_workflow_uses_secret_inheritance_or_auto_merge() -> None:
    for workflow in Path(".github/workflows").glob("*.yml"):
        text = workflow.read_text(encoding="utf-8")
        assert "secrets: inherit" not in text
        assert "gh pr merge" not in text
        assert "--auto" not in text
        assert "ready_for_review" not in text


@pytest.mark.parametrize(
    "mutator,error",
    [
        (
            lambda d: d["target"].update(repository="Young-Consultations/other"),
            "target repository",
        ),
        (lambda d: d["governance"].update(approved=False), "approved"),
        (lambda d: d["task"].update(sensitive=True), "sensitive"),
        (lambda d: d["source"].update(issue_state="closed"), "open"),
    ],
)
def test_slugger_target_policy_rejects_unauthorized_inputs(mutator, error) -> None:
    data = _canonical()
    mutator(data)
    with pytest.raises(TargetPolicyError, match=error):
        authorize_slugger_execution(data)


def test_slugger_target_policy_preserves_canonical_identities() -> None:
    plan = authorize_slugger_execution(_canonical(mode="implement"))
    assert plan.task_id == "task-123"
    assert plan.correlation_id == "corr-123"
    assert plan.delivery_id == "delivery-123"
    assert plan.publication_identity == "delivery-123"
    assert plan.requested_branch == deterministic_branch("delivery-123")
    assert plan.mode == "implement"


def test_pinned_v2_contract_uses_stable_publication_identity_for_delivery() -> None:
    data = _canonical(mode="implement")
    data.pop("contract_version")
    data.pop("delivery_id")
    data.pop("requested_branch")
    data["publication"]["identity"] = "v2-publication-123"

    plan = authorize_slugger_execution(data)

    assert plan.contract_version == "ai-sdlc-contract/v2"
    assert plan.delivery_id == "v2-publication-123"
    assert plan.publication_identity == "v2-publication-123"
    assert plan.requested_branch == deterministic_branch("v2-publication-123")


def test_verify_mode_cannot_mutate_git_or_publish() -> None:
    verify = _workflow(TARGET_WORKFLOW)["jobs"]["verify"]
    text = str(verify)
    assert verify["permissions"] == {"contents": "read"}
    assert "openai/codex-action" not in text
    assert "git checkout" not in text
    assert "git push" not in text
    assert "gh pr create" not in text
    assert '"occurred": False' in TARGET_WORKFLOW.read_text(encoding="utf-8")


def test_verify_mode_installs_contracts_before_result_validation() -> None:
    verify = _workflow(TARGET_WORKFLOW)["jobs"]["verify"]
    step_names = [step.get("name", "") for step in verify["steps"]]
    install_index = step_names.index(
        "Install organization contracts for result validation"
    )
    emit_index = step_names.index("Emit and validate canonical result")
    assert install_index < emit_index
    checkout_step = verify["steps"][1]
    assert checkout_step["with"]["repository"] == "Young-Consultations/.github"
    assert checkout_step["with"]["path"] == ".ai-sdlc-control-plane"
    verify_text = str(verify)
    assert 'python -m pip install -e "./.ai-sdlc-control-plane"' in verify_text
    assert "validate_execution_result" in verify_text


def test_implement_mode_is_gated_and_publishes_only_an_owned_draft() -> None:
    data = _workflow(TARGET_WORKFLOW)
    implement = data["jobs"]["implement"]
    assert "new-delivery" in implement["if"]
    assert "resume-incomplete-delivery" in implement["if"]
    text = TARGET_WORKFLOW.read_text(encoding="utf-8")
    assert "openai/codex-action" in str(implement)
    assert "slugger-canonical-delivery" in Path("mvp/codex_target.py").read_text()
    assert "gh pr create" in text and "--draft" in text
    assert "gh pr merge" not in text


def test_old_issue_bridge_cannot_silently_return_as_supported_path() -> None:
    text = "\n".join(
        p.read_text(encoding="utf-8") for p in Path(".github/workflows").glob("*.yml")
    )
    assert "mvp.issue_bridge" not in text
    assert "issue-to-codex" not in text
    assert "AUTHORIZED_CODEX_READY_ACTORS" not in text
