from pathlib import Path

import pytest
import yaml

from mvp.issue_bridge import (
    IssueBridgeError,
    actor_is_authorized,
    load_allowlist,
    parse_issue_contract,
)

ISSUE_WORKFLOW = Path(".github/workflows/issue-to-codex.yml")
USER_IDEA_WORKFLOW = Path(".github/workflows/user-idea-codex-cli-demo.yml")
ALLOWLIST = Path(".github/slugger/target-allowlist.json")


def _workflow(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _body(repo: str = "Young-Consultations/slugger-generated-demos") -> str:
    return f"""<!-- portfolio-task-source: Young-Consultations/portfolio-tasks#123 -->
<!-- slugger-field: idea -->Build a tiny calculator CLI.<!-- /slugger-field: idea -->
<!-- slugger-field: project_name -->calculator-demo<!-- /slugger-field: project_name -->
<!-- slugger-field: target_repository -->{repo}<!-- /slugger-field: target_repository -->
"""


def test_issue_bridge_triggers_only_on_codex_ready_labeled_issues() -> None:
    data = _workflow(ISSUE_WORKFLOW)
    assert data[True] == {"issues": {"types": ["labeled"]}}
    assert data["jobs"]["preflight"]["if"] == "github.event.label.name == 'codex-ready'"
    text = ISSUE_WORKFLOW.read_text(encoding="utf-8")
    assert "chatgpt-task" not in text
    assert "portfolio-task" not in text
    assert "pull_request_target" not in text
    assert "issue_comment" not in text


def test_issue_contract_accepts_only_eligible_issues() -> None:
    allowlist = load_allowlist(ALLOWLIST)
    contract = parse_issue_contract(
        body=_body(),
        issue_number=7,
        issue_url="https://github.com/o/r/issues/7",
        allowlist=allowlist,
    )
    assert contract.target_repository == "Young-Consultations/slugger-generated-demos"
    assert len(contract.request_identity) == 64


@pytest.mark.parametrize(
    "body,error",
    [
        ("", "missing portfolio task source marker"),
        (
            _body().replace("portfolio-task-source", "chatgpt-task-source"),
            "unsupported legacy source marker",
        ),
        (
            _body().replace(
                "<!-- slugger-field: idea -->Build a tiny calculator CLI.<!-- /slugger-field: idea -->",
                "",
            ),
            "missing required field: idea",
        ),
        (
            _body("Young-Consultations/not-allowed"),
            "target repository is not allowlisted",
        ),
        (_body("not-owner-repo"), "target repository must use owner/repository format"),
    ],
)
def test_issue_contract_rejects_invalid_or_unsupported_inputs(
    body: str, error: str
) -> None:
    with pytest.raises(IssueBridgeError, match=error):
        parse_issue_contract(
            body=body,
            issue_number=7,
            issue_url="https://github.com/o/r/issues/7",
            allowlist=load_allowlist(ALLOWLIST),
        )


def test_authorized_actors_are_explicitly_configured() -> None:
    assert actor_is_authorized("maintainer", "owner, maintainer") is True
    assert actor_is_authorized("intruder", "owner, maintainer") is False


def test_issue_workflow_prevents_duplicates_and_updates_state_labels() -> None:
    text = ISSUE_WORKFLOW.read_text(encoding="utf-8")
    data = _workflow(ISSUE_WORKFLOW)
    assert data["concurrency"] == {
        "group": "issue-to-codex-${{ github.repository }}-${{ github.event.issue.number }}",
        "cancel-in-progress": False,
    }
    assert "An active or completed execution already exists" in text
    assert "--add-label codex-running" in text
    assert "--remove-label codex-running" in text
    assert 'RESULT_LABEL="codex-complete"' in text
    assert 'RESULT_LABEL="codex-failed"' in text
    assert '--add-label "$RESULT_LABEL"' in text
    assert "--add-label codex-ready" not in text


def test_issue_workflow_fails_closed_before_codex_generation() -> None:
    text = ISSUE_WORKFLOW.read_text(encoding="utf-8")
    assert "ISSUE_PULL_REQUEST" in text
    assert "Issue-to-Codex accepts issues only; pull requests are rejected." in text
    assert (
        "missing portfolio task source marker" not in text
    )  # message comes from helper, not shell parsing
    assert "AUTHORIZED_CODEX_READY_ACTORS" in text
    assert "Issue-to-Codex must run from the default branch." in text
    assert "SLUGGER_TARGET_ALLOWLIST: .github/slugger/target-allowlist.json" in text


def test_issue_workflow_reuses_canonical_user_idea_workflow() -> None:
    data = _workflow(ISSUE_WORKFLOW)
    call = data["jobs"]["run-canonical-codex"]
    assert call["uses"] == "./.github/workflows/user-idea-codex-cli-demo.yml"
    assert "openai/codex-action" not in str(data["jobs"]["preflight"])
    assert "openai/codex-action" not in str(data["jobs"]["report-result"])


def test_report_result_uses_explicit_repo_context_without_checkout() -> None:
    data = _workflow(ISSUE_WORKFLOW)
    report = data["jobs"]["report-result"]
    assert all(
        step.get("uses") != "actions/checkout@93cb6efe18208431cddfb8368fd83d5badbf9bfd"
        for step in report["steps"]
    )
    step = report["steps"][0]
    assert step["env"]["GH_REPO"] == "${{ github.repository }}"
    assert "GH_REPO" in str(step)
    assert "gh issue edit" in step["run"]
    assert "gh issue comment" in step["run"]


def test_report_result_has_no_malformed_heredoc_and_best_effort_actions() -> None:
    data = _workflow(ISSUE_WORKFLOW)
    run = data["jobs"]["report-result"]["steps"][0]["run"]
    assert "cat > issue-comment.md <<EOF" not in run
    assert "run_report_action" in run
    assert "--remove-label codex-running" in run
    assert '--add-label "$RESULT_LABEL"' in run
    assert "codex-complete" in run
    assert "codex-failed" in run
    assert "Every Slugger issue reporting action failed." in run


def test_report_result_success_and_failure_comments_are_markdown() -> None:
    run = _workflow(ISSUE_WORKFLOW)["jobs"]["report-result"]["steps"][0]["run"]
    assert "### Slugger Codex automation complete" in run
    assert "### Slugger Codex automation failed" in run
    assert "- Workflow run URL:" in run
    assert "- Completion status: codex-complete" in run
    assert "- Failed phase: canonical-user-idea-workflow" in run
    assert "Slugger request identity:" in run


def test_result_comments_are_bounded_and_secret_safe() -> None:
    text = ISSUE_WORKFLOW.read_text(encoding="utf-8")
    assert "Workflow run URL" in text
    assert "Draft pull request URL" in text
    assert "Manifest digest" in text
    assert "head -c 500" in text
    assert "OPENAI_API_KEY" not in text
    assert "SLUGGER_GITHUB_TOKEN" not in text
    assert "Authorization:" not in text


def test_manual_dispatch_and_workflow_call_share_user_idea_jobs() -> None:
    data = _workflow(USER_IDEA_WORKFLOW)
    assert set(data[True]) == {"workflow_dispatch", "workflow_call"}
    assert data[True]["workflow_dispatch"]["inputs"]["idea"]["required"] is True
    assert data[True]["workflow_call"]["inputs"]["idea"]["required"] is True
    assert "generate-with-codex" in data["jobs"]
    assert "openai/codex-action" in USER_IDEA_WORKFLOW.read_text(encoding="utf-8")
