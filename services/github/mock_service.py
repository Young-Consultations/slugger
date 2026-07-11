"""Mock GitHub service."""

from __future__ import annotations

from services.github.base import IGitHubService
from services.github.models import (
    GitHubComment,
    GitHubIssue,
    GitHubMilestone,
    GitHubPR,
    GitHubRelease,
    GitHubRepo,
    GitHubWorkflowRun,
)


class MockGitHubService(IGitHubService):
    def __init__(self) -> None:
        self.repo = GitHubRepo(owner='slugger', name='slugger')
        self.issues: list[GitHubIssue] = []
        self.pull_requests: list[GitHubPR] = []
        self.comments: dict[int, list[GitHubComment]] = {}
        self.milestones: list[GitHubMilestone] = []
        self.releases: list[GitHubRelease] = []
        self.workflow_runs: list[GitHubWorkflowRun] = []
        self.triggered_workflows: list[dict[str, object]] = []
        self._next_issue = 1
        self._next_pr = 1
        self._next_milestone = 1

    def get_repo(self) -> GitHubRepo:
        return self.repo

    def list_issues(self) -> list[GitHubIssue]:
        return list(self.issues)

    def list_pull_requests(self) -> list[GitHubPR]:
        return list(self.pull_requests)

    def create_comment(self, issue_number: int, comment: GitHubComment) -> GitHubComment:
        self.comments.setdefault(issue_number, []).append(comment)
        return comment

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
        milestone_number: int | None = None,
    ) -> GitHubIssue:
        issue = GitHubIssue(
            number=self._next_issue,
            title=title,
            body=body,
            labels=labels or [],
            milestone_number=milestone_number,
        )
        self._next_issue += 1
        self.issues.append(issue)
        return issue

    def create_pull_request(self, title: str, body: str, head: str, base: str = 'main') -> GitHubPR:
        pr = GitHubPR(
            number=self._next_pr,
            title=title,
            body=body,
            head=head,
            base=base,
        )
        self._next_pr += 1
        self.pull_requests.append(pr)
        return pr

    def list_milestones(self) -> list[GitHubMilestone]:
        return list(self.milestones)

    def create_milestone(self, title: str, description: str = '', due_on: str | None = None) -> GitHubMilestone:
        milestone = GitHubMilestone(
            number=self._next_milestone,
            title=title,
            description=description,
            due_on=due_on,
        )
        self._next_milestone += 1
        self.milestones.append(milestone)
        return milestone

    def list_releases(self) -> list[GitHubRelease]:
        return list(self.releases)

    def create_release(
        self,
        tag_name: str,
        name: str,
        body: str = '',
        draft: bool = False,
        prerelease: bool = False,
    ) -> GitHubRelease:
        release = GitHubRelease(
            tag_name=tag_name,
            name=name,
            body=body,
            draft=draft,
            prerelease=prerelease,
        )
        self.releases.append(release)
        return release

    def list_workflow_runs(self, workflow_id: str | int | None = None) -> list[GitHubWorkflowRun]:
        if workflow_id is not None:
            workflow_id_str = str(workflow_id)
            return [run for run in self.workflow_runs if str(run.workflow_id) == workflow_id_str]
        return list(self.workflow_runs)

    def trigger_workflow(self, workflow_id: str, ref: str = 'main', inputs: dict[str, str] | None = None) -> None:
        self.triggered_workflows.append({'workflow_id': workflow_id, 'ref': ref, 'inputs': inputs or {}})

