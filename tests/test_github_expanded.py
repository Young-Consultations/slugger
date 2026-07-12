"""Tests for Epic 1: expanded GitHub integration."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from services.github import (
    GitHubIssue,
    GitHubMilestone,
    GitHubPR,
    GitHubRelease,
    GitHubWorkflowRun,
    IGitHubService,
    MockGitHubService,
)


@pytest.fixture()
def svc() -> MockGitHubService:
    return MockGitHubService()


def test_mock_implements_interface() -> None:
    assert issubclass(MockGitHubService, IGitHubService)


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------


def test_create_issue(svc: MockGitHubService) -> None:
    issue = svc.create_issue(
        "Bug: null pointer", "Steps to reproduce...", labels=["bug"]
    )
    assert isinstance(issue, GitHubIssue)
    assert issue.number == 1
    assert issue.title == "Bug: null pointer"
    assert "bug" in issue.labels


def test_create_issue_increments_number(svc: MockGitHubService) -> None:
    i1 = svc.create_issue("Issue 1", "body")
    i2 = svc.create_issue("Issue 2", "body")
    assert i2.number == i1.number + 1


def test_list_issues_after_create(svc: MockGitHubService) -> None:
    svc.create_issue("A", "body")
    svc.create_issue("B", "body")
    assert len(svc.list_issues()) == 2


# ---------------------------------------------------------------------------
# Pull Requests
# ---------------------------------------------------------------------------


def test_create_pull_request(svc: MockGitHubService) -> None:
    pr = svc.create_pull_request("Add feature X", "description", head="feature-x")
    assert isinstance(pr, GitHubPR)
    assert pr.number == 1
    assert pr.head == "feature-x"
    assert pr.base == "main"


def test_list_pull_requests_after_create(svc: MockGitHubService) -> None:
    svc.create_pull_request("PR 1", "", head="branch-1")
    assert len(svc.list_pull_requests()) == 1


def test_github_service_creates_draft_pr_not_merged(svc: MockGitHubService) -> None:
    pr = svc.create_pull_request(
        "Draft feature", "description", head="feature-draft", draft=True
    )
    assert pr.draft is True
    assert pr.merged is False
    assert pr.state == "open"


def test_ci_yml_exists_and_valid() -> None:
    workflow_path = Path(".github/workflows/ci.yml")
    assert workflow_path.exists()
    with workflow_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["name"] == "CI"
    assert "jobs" in data
    assert "test" in data["jobs"]


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------


def test_create_milestone(svc: MockGitHubService) -> None:
    ms = svc.create_milestone(
        "v1.0", description="First release", due_on="2026-12-31T00:00:00Z"
    )
    assert isinstance(ms, GitHubMilestone)
    assert ms.number == 1
    assert ms.title == "v1.0"
    assert ms.due_on == "2026-12-31T00:00:00Z"


def test_list_milestones(svc: MockGitHubService) -> None:
    svc.create_milestone("v0.1")
    svc.create_milestone("v0.2")
    assert len(svc.list_milestones()) == 2


def test_create_milestone_increments_number(svc: MockGitHubService) -> None:
    m1 = svc.create_milestone("M1")
    m2 = svc.create_milestone("M2")
    assert m2.number == m1.number + 1


# ---------------------------------------------------------------------------
# Releases
# ---------------------------------------------------------------------------


def test_create_release(svc: MockGitHubService) -> None:
    rel = svc.create_release("v1.0.0", "Release 1.0.0", body="Initial release.")
    assert isinstance(rel, GitHubRelease)
    assert rel.tag_name == "v1.0.0"
    assert rel.draft is False
    assert rel.prerelease is False


def test_create_draft_release(svc: MockGitHubService) -> None:
    rel = svc.create_release("v2.0.0-rc1", "Release Candidate", draft=True)
    assert rel.draft is True


def test_list_releases(svc: MockGitHubService) -> None:
    svc.create_release("v1.0.0", "R1")
    svc.create_release("v1.1.0", "R2")
    assert len(svc.list_releases()) == 2


# ---------------------------------------------------------------------------
# Workflow runs & dispatch
# ---------------------------------------------------------------------------


def test_trigger_workflow(svc: MockGitHubService) -> None:
    svc.trigger_workflow("ci.yml", ref="main", inputs={"env": "prod"})
    assert len(svc.triggered_workflows) == 1
    triggered = svc.triggered_workflows[0]
    assert triggered["workflow_id"] == "ci.yml"
    assert triggered["ref"] == "main"
    assert triggered["inputs"] == {"env": "prod"}


def test_list_workflow_runs_empty(svc: MockGitHubService) -> None:
    assert svc.list_workflow_runs() == []


def test_list_workflow_runs_with_runs(svc: MockGitHubService) -> None:
    svc.workflow_runs = [
        GitHubWorkflowRun(
            id=1, name="CI", status="completed", conclusion="success", workflow_id=10
        ),
        GitHubWorkflowRun(id=2, name="Deploy", status="in_progress", workflow_id=20),
    ]
    assert len(svc.list_workflow_runs()) == 2


def test_list_workflow_runs_filter_by_workflow(svc: MockGitHubService) -> None:
    svc.workflow_runs = [
        GitHubWorkflowRun(id=1, name="CI", workflow_id=10),
        GitHubWorkflowRun(id=2, name="CI", workflow_id=10),
        GitHubWorkflowRun(id=3, name="Deploy", workflow_id=20),
    ]
    ci_runs = svc.list_workflow_runs(workflow_id=10)
    assert len(ci_runs) == 2
    deploy_runs = svc.list_workflow_runs(workflow_id=20)
    assert len(deploy_runs) == 1
