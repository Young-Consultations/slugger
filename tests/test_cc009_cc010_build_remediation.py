"""CC-009 and CC-010: Build runner and remediation loop tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from materializer import (
    BuildPhase,
    BuildResult,
    CommandEvidence,
    FakeIsolatedBuildRunner,
    PhaseStatus,
    ProjectMaterializer,
)
from models.app_manifest import make_cli_manifest
from validators.remediation import (
    BoundedRemediationLoop,
    Finding,
    FindingCategory,
    FindingSeverity,
    FindingStatus,
)


# ---------------------------------------------------------------------------
# CC-009: Build runner tests
# ---------------------------------------------------------------------------

class TestFakeIsolatedBuildRunner:
    def test_all_phases_pass(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, ['python -m pytest tests/ -q'], app_id='app-1')
        assert result.overall_success is True
        assert all(p.passed for p in result.phases)

    def test_fail_specific_phase(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner(fail_phases={BuildPhase.TEST})
        result = runner.run(tmp_path, ['python -m pytest tests/ -q'], app_id='app-1')
        assert result.overall_success is False
        test_phase = result.phase_result(BuildPhase.TEST)
        assert test_phase.status == PhaseStatus.FAILED

    def test_records_calls(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner()
        runner.run(tmp_path, ['python -m pytest tests/'], app_id='app-1')
        assert len(runner.calls) == 1
        assert runner.calls[0]['app_id'] == 'app-1'

    def test_all_phases_present(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, [], app_id='app-1')
        phases = {p.phase for p in result.phases}
        assert BuildPhase.INSTALL in phases
        assert BuildPhase.TEST in phases

    def test_evidence_attached_to_phase(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, ['python -m pytest'], app_id='app-1')
        install = result.phase_result(BuildPhase.INSTALL)
        assert len(install.evidence) >= 1

    def test_command_evidence_fields(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner()
        result = runner.run(tmp_path, ['python -m pytest'], app_id='app-1')
        e = result.phase_result(BuildPhase.INSTALL).evidence[0]
        assert hasattr(e, 'exit_code')
        assert hasattr(e, 'stdout')
        assert hasattr(e, 'stderr')
        assert hasattr(e, 'duration_ms')


class TestCommandEvidence:
    def test_passed_when_exit_code_zero(self) -> None:
        e = CommandEvidence(command='test', exit_code=0, stdout='ok', stderr='', duration_ms=1.0)
        assert e.passed is True

    def test_failed_when_exit_code_nonzero(self) -> None:
        e = CommandEvidence(command='test', exit_code=1, stdout='', stderr='fail', duration_ms=1.0)
        assert e.passed is False

    def test_failed_when_timed_out(self) -> None:
        e = CommandEvidence(command='test', exit_code=0, stdout='', stderr='', duration_ms=120000.0, timed_out=True)
        assert e.passed is False


class TestBuildRunnerIntegration:
    def test_materializer_and_runner_integration(self, tmp_path: Path) -> None:
        """Materialize a manifest, then run the fake build runner on the workspace."""
        mat = ProjectMaterializer(tmp_path / 'workspaces')
        manifest = make_cli_manifest('app-1', 'MyApp', 'task tracker')
        mat_result = mat.materialize(manifest)
        assert mat_result.success

        runner = FakeIsolatedBuildRunner()
        build_result = runner.run(mat_result.workspace.root, manifest.commands, app_id='app-1')
        assert build_result.overall_success is True

    def test_broken_workspace_fails_build(self, tmp_path: Path) -> None:
        runner = FakeIsolatedBuildRunner(fail_phases={BuildPhase.TEST, BuildPhase.INSTALL})
        result = runner.run(tmp_path, ['python -m pytest'], app_id='broken-app')
        assert result.overall_success is False


# ---------------------------------------------------------------------------
# CC-010: Bounded remediation loop tests
# ---------------------------------------------------------------------------

def _finding(fid: str, severity=FindingSeverity.MEDIUM, category=FindingCategory.CODE_REVIEW) -> Finding:
    return Finding(
        finding_id=fid,
        severity=severity,
        category=category,
        message='Test finding',
        waiver_eligible=True,
    )


class TestFinding:
    def test_high_severity_is_blocking(self) -> None:
        f = _finding('f1', FindingSeverity.HIGH)
        assert f.is_blocking is True

    def test_medium_not_blocking(self) -> None:
        f = _finding('f1', FindingSeverity.MEDIUM)
        assert f.is_blocking is False

    def test_critical_security_requires_human_waiver(self) -> None:
        f = _finding('f1', FindingSeverity.CRITICAL, FindingCategory.SECURITY)
        assert f.requires_human_waiver is True

    def test_medium_code_review_does_not_require_human_waiver(self) -> None:
        f = _finding('f1', FindingSeverity.MEDIUM, FindingCategory.CODE_REVIEW)
        assert f.requires_human_waiver is False


class TestBoundedRemediationLoop:
    def test_all_resolved_when_attempt_fn_succeeds(self) -> None:
        loop = BoundedRemediationLoop()
        findings = [_finding('f1'), _finding('f2')]
        result = loop.process(findings, attempt_fn=lambda f: True)
        assert result.all_resolved is True
        assert len(result.resolved_findings) == 2

    def test_escalated_when_attempt_fn_always_fails(self) -> None:
        loop = BoundedRemediationLoop()
        findings = [_finding('f1', FindingSeverity.HIGH)]
        result = loop.process(findings, attempt_fn=lambda f: False)
        assert result.all_resolved is False
        assert result.requires_manual_intervention is True

    def test_no_attempt_fn_classifies_without_resolving(self) -> None:
        loop = BoundedRemediationLoop()
        findings = [_finding('f1')]
        result = loop.process(findings, attempt_fn=None)
        # Without attempt_fn, findings should be categorised but open
        assert len(result.resolved_findings) == 0

    def test_bounded_attempts_count(self) -> None:
        loop = BoundedRemediationLoop(max_attempts={FindingCategory.CODE_REVIEW: 2})
        attempt_count = {'n': 0}
        def always_fail(f):
            attempt_count['n'] += 1
            return False
        findings = [_finding('f1', FindingSeverity.MEDIUM, FindingCategory.CODE_REVIEW)]
        loop.process(findings, attempt_fn=always_fail)
        assert attempt_count['n'] <= 2

    def test_waive_low_severity_succeeds(self) -> None:
        loop = BoundedRemediationLoop()
        f = _finding('f1', FindingSeverity.LOW)
        success = loop.waive(f, approver='')
        assert success
        assert f.status == FindingStatus.WAIVED

    def test_waive_critical_security_requires_approver(self) -> None:
        loop = BoundedRemediationLoop()
        f = _finding('f1', FindingSeverity.CRITICAL, FindingCategory.SECURITY)
        success = loop.waive(f, approver='')
        assert success is False
        assert f.status != FindingStatus.WAIVED

    def test_waive_critical_security_with_approver_succeeds(self) -> None:
        loop = BoundedRemediationLoop()
        f = _finding('f1', FindingSeverity.CRITICAL, FindingCategory.SECURITY)
        success = loop.waive(f, approver='security-officer')
        assert success
        assert f.status == FindingStatus.WAIVED

    def test_all_findings_have_lifecycle_status(self) -> None:
        loop = BoundedRemediationLoop()
        findings = [
            _finding('f1', FindingSeverity.LOW),
            _finding('f2', FindingSeverity.HIGH),
        ]
        result = loop.process(findings, attempt_fn=lambda f: f.severity == FindingSeverity.LOW)
        for f in findings:
            assert f.status != FindingStatus.OPEN

    def test_attempts_recorded_in_result(self) -> None:
        loop = BoundedRemediationLoop()
        findings = [_finding('f1')]
        result = loop.process(findings, attempt_fn=lambda f: True)
        assert len(result.attempts) >= 1
        assert result.attempts[0].finding_id == 'f1'
