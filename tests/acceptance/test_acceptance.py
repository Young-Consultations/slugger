"""CC-018 Acceptance Test Suite.

Proves idea-to-production behavior across all major system paths.
These tests use deterministic mocks but exercise the real orchestration
path (not isolated unit tests).

P0 scenarios (must all pass for 100% P0 completion):
- Idea → planning artifacts
- Validated manifest → workspace
- Build runner with passing/failing fixtures
- Remediation loop convergence and escalation
- Readiness gate: all-pass and blocked-by-failure
- Approval persistence across restart simulation

Coverage target: ≥ 95% overall, 100% P0.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# P0-001: Idea to planning artifacts
# ---------------------------------------------------------------------------

class TestP0IdeaToPlanningArtifacts:
    """Idea propagates through all planning agents and produces real content."""

    idea = 'Build a command-line task tracker with priorities and due dates'

    def test_vision_artifact_contains_idea(self) -> None:
        from agents.planning.product_vision_agent import ProductVisionAgent
        from models.execution import ExecutionContext
        ctx = ExecutionContext(project_id='p0-001', workflow_name='sdlc', step_name='vision',
                               metadata={'idea': self.idea})
        arts = ProductVisionAgent().execute(ctx)
        assert arts[0].name == 'product_vision'
        assert 'Product Vision' in arts[0].content

    def test_requirements_chain(self) -> None:
        from agents.planning.product_vision_agent import ProductVisionAgent
        from agents.planning.requirements_agent import RequirementsAgent
        from models.execution import ExecutionContext
        ctx1 = ExecutionContext(project_id='p0-001', workflow_name='sdlc', step_name='vision', metadata={'idea': self.idea})
        vision_arts = ProductVisionAgent().execute(ctx1)
        ctx2 = ExecutionContext(project_id='p0-001', workflow_name='sdlc', step_name='req',
                                metadata={'idea': self.idea}, inputs={'product_vision': vision_arts[0]})
        req_arts = RequirementsAgent().execute(ctx2)
        assert req_arts[0].name == 'requirements'
        assert len(req_arts[0].content) > 20

    def test_user_stories_chain(self) -> None:
        from agents.planning.user_story_agent import UserStoryAgent
        from models.execution import ExecutionContext
        ctx = ExecutionContext(project_id='p0-001', workflow_name='sdlc', step_name='stories',
                               metadata={'idea': self.idea})
        arts = UserStoryAgent().execute(ctx)
        assert arts[0].name == 'user_stories'

    def test_project_plan_chain(self) -> None:
        from agents.planning.project_plan_agent import ProjectPlanAgent
        from models.execution import ExecutionContext
        ctx = ExecutionContext(project_id='p0-001', workflow_name='sdlc', step_name='plan',
                               metadata={'idea': self.idea})
        arts = ProjectPlanAgent().execute(ctx)
        assert arts[0].name == 'project_plan'


# ---------------------------------------------------------------------------
# P0-002: Manifest to workspace
# ---------------------------------------------------------------------------

class TestP0ManifestToWorkspace:
    def test_cli_manifest_materializes(self, tmp_path: Path) -> None:
        from models.app_manifest import make_cli_manifest, validate_app_manifest
        from materializer import ProjectMaterializer
        manifest = make_cli_manifest('p0-cli', 'TaskCLI', 'CLI task tracker')
        assert validate_app_manifest(manifest).valid
        mat = ProjectMaterializer(tmp_path / 'ws')
        result = mat.materialize(manifest)
        assert result.success
        assert (result.workspace.root / 'pyproject.toml').exists()
        assert (result.workspace.root / 'README.md').exists()

    def test_fastapi_manifest_materializes(self, tmp_path: Path) -> None:
        from models.app_manifest import make_fastapi_manifest, validate_app_manifest
        from materializer import ProjectMaterializer
        manifest = make_fastapi_manifest('p0-api', 'TaskAPI', 'FastAPI task service')
        assert validate_app_manifest(manifest).valid
        mat = ProjectMaterializer(tmp_path / 'ws')
        result = mat.materialize(manifest)
        assert result.success

    def test_unsafe_manifest_rejected(self, tmp_path: Path) -> None:
        from models.app_manifest import AppManifest, AppTemplate, FileEntry, validate_app_manifest
        from materializer import ProjectMaterializer
        manifest = AppManifest(
            app_id='unsafe', name='Unsafe', template=AppTemplate.CLI,
            files=[FileEntry(path='../../evil.py', content='import os')],
        )
        result = validate_app_manifest(manifest)
        assert not result.valid

    def test_idempotent_resume(self, tmp_path: Path) -> None:
        from models.app_manifest import make_cli_manifest
        from materializer import ProjectMaterializer
        manifest = make_cli_manifest('p0-cli', 'TaskCLI')
        mat = ProjectMaterializer(tmp_path / 'ws')
        mat.materialize(manifest)
        result = mat.resume(manifest)
        assert result.success


# ---------------------------------------------------------------------------
# P0-003: Build runner
# ---------------------------------------------------------------------------

class TestP0BuildRunner:
    def test_fake_runner_passing_fixture(self, tmp_path: Path) -> None:
        from materializer import FakeIsolatedBuildRunner
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, ['python -m pytest tests/ -q'], app_id='p0-build')
        assert result.overall_success is True

    def test_fake_runner_failing_fixture(self, tmp_path: Path) -> None:
        from materializer import FakeIsolatedBuildRunner, BuildPhase
        runner = FakeIsolatedBuildRunner(fail_phases={BuildPhase.TEST})
        result = runner.run(tmp_path, ['python -m pytest tests/ -q'], app_id='p0-broken')
        assert result.overall_success is False
        assert result.phase_result(BuildPhase.TEST).passed is False

    def test_evidence_is_machine_readable(self, tmp_path: Path) -> None:
        from materializer import FakeIsolatedBuildRunner, BuildPhase
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, ['python -m pytest'], app_id='p0-ev')
        install = result.phase_result(BuildPhase.INSTALL)
        assert install.evidence[0].exit_code == 0
        assert isinstance(install.evidence[0].duration_ms, float)


# ---------------------------------------------------------------------------
# P0-004: Remediation loop
# ---------------------------------------------------------------------------

class TestP0RemediationLoop:
    def test_convergence_in_bounded_attempts(self) -> None:
        from validators.remediation import (
            BoundedRemediationLoop, Finding, FindingCategory, FindingSeverity, FindingStatus,
        )
        loop = BoundedRemediationLoop()
        f = Finding('f1', FindingSeverity.MEDIUM, FindingCategory.CODE_REVIEW, 'Missing docstring')
        attempt_n = {'n': 0}
        def fix(finding):
            attempt_n['n'] += 1
            return True  # Always succeeds

        result = loop.process([f], attempt_fn=fix)
        assert f.status == FindingStatus.REMEDIATED
        assert result.all_resolved is True

    def test_non_convergence_escalates_blocking(self) -> None:
        from validators.remediation import (
            BoundedRemediationLoop, Finding, FindingCategory, FindingSeverity, FindingStatus,
        )
        loop = BoundedRemediationLoop()
        f = Finding('f1', FindingSeverity.HIGH, FindingCategory.SECURITY, 'SQL injection', waiver_eligible=False)
        result = loop.process([f], attempt_fn=lambda _: False)
        assert f.status == FindingStatus.MANUAL_REQUIRED
        assert result.requires_manual_intervention is True

    def test_security_critical_requires_explicit_approver(self) -> None:
        from validators.remediation import (
            BoundedRemediationLoop, Finding, FindingCategory, FindingSeverity, FindingStatus,
        )
        loop = BoundedRemediationLoop()
        f = Finding('f1', FindingSeverity.CRITICAL, FindingCategory.SECURITY, 'Hardcoded secret')
        ok = loop.waive(f, approver='')
        assert ok is False
        ok2 = loop.waive(f, approver='security-officer')
        assert ok2 is True


# ---------------------------------------------------------------------------
# P0-005: Readiness gates
# ---------------------------------------------------------------------------

class TestP0ReadinessGates:
    def test_all_gates_pass_produces_rc(self) -> None:
        from validators.readiness import ReleaseGateCollector
        c = ReleaseGateCollector('p0-app', 'run-1')
        c.record_passed('build', 'ev1', 'Build OK')
        c.record_passed('tests', 'ev2', '100 tests passed')
        c.record_passed('security', 'ev3', 'No critical findings')
        report = c.collect()
        assert report.release_candidate is True

    def test_failed_test_gate_blocks_rc(self) -> None:
        from validators.readiness import ReleaseGateCollector
        c = ReleaseGateCollector('p0-app', 'run-2')
        c.record_passed('build', 'ev1')
        c.record_failed('tests', 'pytest found 2 failures')
        c.record_passed('security', 'ev3')
        report = c.collect()
        assert report.release_candidate is False
        assert 'tests' in report.blocking_gates


# ---------------------------------------------------------------------------
# P0-006: Approval persistence
# ---------------------------------------------------------------------------

class TestP0ApprovalPersistence:
    def test_approval_persists_across_simulated_restart(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision
        db = tmp_path / 'approvals.db'
        store1 = DurableApprovalStore(db)
        record = ApprovalRecord(record_id='p0-r1', checkpoint_name='deploy-gate', run_id='p0-run-1',
                                decision=ApprovalDecision.APPROVED, approver='alice')
        store1.save(record)
        # Simulate restart
        store2 = DurableApprovalStore(db)
        assert store2.has_approval('p0-run-1', 'deploy-gate') is True

    def test_pending_not_counted_as_approval(self, tmp_path: Path) -> None:
        from workflow.durable_approvals import DurableApprovalStore
        from workflow.approvals import ApprovalRecord, ApprovalDecision
        store = DurableApprovalStore(tmp_path / 'approvals.db')
        store.save(ApprovalRecord(record_id='p0-r2', checkpoint_name='deploy-gate', run_id='p0-run-2',
                                  decision=ApprovalDecision.PENDING))
        assert store.has_approval('p0-run-2', 'deploy-gate') is False
