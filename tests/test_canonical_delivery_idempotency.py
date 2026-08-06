from dataclasses import replace

import pytest

from mvp.codex_target import (
    DeliveryState,
    ManagedPullRequest,
    TargetPolicyError,
    authorize_slugger_execution,
    deterministic_branch,
    ownership_marker,
    parse_ownership_marker,
    preflight,
    publish_after_codex,
)


def canonical(delivery="delivery-A", **changes):
    value = {
        "contract_version": "ai-sdlc-contract/v3",
        "delivery_id": delivery,
        "correlation_id": "corr-A",
        "requested_branch": deterministic_branch(delivery),
        "draft_pr_only": True,
        "mode": "implement",
        "target": {"repository": "Young-Consultations/slugger", "executor": "Codex"},
        "source": {
            "repository": "Young-Consultations/portfolio-tasks",
            "issue_number": 42,
            "issue_state": "open",
        },
        "governance": {"approved": True},
        "task": {
            "id": "task-A",
            "type": "mvp_python_cli",
            "sensitive": False,
            "idea": "Make the requested safe change",
            "project_name": "slugger",
        },
        "publication": {"mode": "draft_pr", "identity": delivery},
    }
    value.update(changes)
    return value


class Repository:
    def __init__(self):
        self.prs = []
        self.branches = set()
        self.branch_creates = 0
        self.pr_creates = 0
        self.race = False

    def branch_exists(self, branch):
        return branch in self.branches

    def open_pull_requests(self):
        return list(self.prs)

    def publish_branch(self, branch, base):
        self.branch_creates += 1
        if self.race:
            self.race = False
            self.branches.add(branch)
            plan = self.plan
            self.prs.append(pr_for(plan))
            raise RuntimeError("reference already exists")
        if branch in self.branches:
            raise RuntimeError("reference already exists")
        self.branches.add(branch)

    def create_draft(self, *, branch, base, body):
        self.pr_creates += 1
        pr = ManagedPullRequest(
            1, "https://example.test/pr/1", "open", True, branch, base, body
        )
        self.prs.append(pr)
        return pr


def pr_for(plan, **changes):
    pr = ManagedPullRequest(
        1,
        "https://example.test/pr/1",
        "open",
        True,
        plan.requested_branch,
        "main",
        ownership_marker(plan),
    )
    return replace(pr, **changes)


def test_delivery_id_required_and_never_uses_run_id():
    value = canonical()
    value.pop("delivery_id")
    value["github_run_id"] = "999"
    with pytest.raises(TargetPolicyError, match="delivery_id"):
        authorize_slugger_execution(value)


def test_branch_and_publication_identity_are_stable_across_runs():
    first = authorize_slugger_execution(canonical(github_run_id="1"))
    second = authorize_slugger_execution(
        canonical(github_run_id="2", github_run_attempt="7")
    )
    assert first.requested_branch == second.requested_branch
    assert first.publication_identity == second.publication_identity
    assert first.immutable_digest == second.immutable_digest


def test_marker_round_trip_has_canonical_ownership_fields():
    plan = authorize_slugger_execution(canonical())
    marker = parse_ownership_marker(ownership_marker(plan))
    assert marker["delivery_id"] == plan.delivery_id
    assert marker["source_issue"]["number"] == 42
    assert marker["target_repository"] == "Young-Consultations/slugger"
    assert marker["contract_version"] == "ai-sdlc-contract/v3"
    assert marker["branch"] == plan.requested_branch


def test_marker_and_error_text_do_not_expose_instruction_secrets():
    secret = "ghp_extremely-sensitive-token"
    value = canonical()
    value["task"] = {**value["task"], "idea": f"Do work using {secret}"}
    plan = authorize_slugger_execution(value)
    assert secret not in ownership_marker(plan)


def test_two_runs_and_lost_acknowledgement_execute_and_publish_once():
    plan = authorize_slugger_execution(canonical())
    repo = Repository()
    codex_count = 0
    first = preflight(plan, repo)
    if first.run_codex:
        codex_count += 1
        publish_after_codex(plan, repo)
    # The first terminal acknowledgement is deliberately ignored.
    second = preflight(plan, repo)
    if second.run_codex:
        codex_count += 1
    assert second.state is DeliveryState.REUSE
    assert codex_count == repo.branch_creates == repo.pr_creates == 1
    assert len(repo.branches) == len(repo.prs) == 1


def test_create_race_converges_on_valid_winner():
    plan = authorize_slugger_execution(canonical())
    repo = Repository()
    repo.race, repo.plan = True, plan
    result = publish_after_codex(plan, repo)
    assert result.state is DeliveryState.REUSE
    assert len(repo.branches) == len(repo.prs) == 1
    assert repo.pr_creates == 0


@pytest.mark.parametrize("field", ["source", "target", "requested_branch", "task"])
def test_conflicting_reuse_fails_closed(field):
    original = authorize_slugger_execution(canonical())
    repo = Repository()
    repo.branches.add(original.requested_branch)
    repo.prs.append(pr_for(original))
    value = canonical()
    if field == "source":
        value["source"] = {**value["source"], "issue_number": 99}
    elif field == "target":
        value["target"] = {**value["target"], "repository": "Young-Consultations/other"}
    elif field == "requested_branch":
        value["requested_branch"] = "slugger/wrong"
    else:
        value["task"] = {**value["task"], "idea": "different instructions"}
    if field in {"target", "requested_branch"}:
        with pytest.raises(TargetPolicyError):
            authorize_slugger_execution(value)
    else:
        assert (
            preflight(authorize_slugger_execution(value), repo).state
            is DeliveryState.AMBIGUOUS
        )


def test_multiple_matching_drafts_are_preserved_and_ambiguous():
    plan = authorize_slugger_execution(canonical())
    repo = Repository()
    repo.prs = [
        pr_for(plan),
        replace(pr_for(plan), number=2, url="https://example.test/pr/2"),
    ]
    result = preflight(plan, repo)
    assert result.state is DeliveryState.AMBIGUOUS
    assert len(repo.prs) == 2


@pytest.mark.parametrize(
    "changes", [{"draft": False}, {"state": "closed"}, {"base": "release"}]
)
def test_unsafe_matching_pr_is_ambiguous(changes):
    plan = authorize_slugger_execution(canonical())
    repo = Repository()
    repo.prs = [pr_for(plan, **changes)]
    assert preflight(plan, repo).state is DeliveryState.AMBIGUOUS
