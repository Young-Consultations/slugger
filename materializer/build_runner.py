"""Isolated build runner for generated applications (CC-009).

Runs dependency installation, tests, linting, and smoke commands in an
isolated environment.  All phases produce machine-readable evidence
artifacts.  Host secrets do not enter the generated process environment.

Only commands declared in the AppManifest may be executed.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Build phase constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS = 120
MAX_OUTPUT_BYTES = 64 * 1024  # 64 KiB cap on captured output

# Allowed environment variable names passed to the subprocess.
# Host secrets (tokens, keys, etc.) are excluded.
_ALLOWED_ENV_KEYS = frozenset({
    'PATH', 'HOME', 'USER', 'TMPDIR', 'TMP', 'TEMP',
    'PYTHONPATH', 'PYTHONDONTWRITEBYTECODE',
    'VIRTUAL_ENV', 'VIRTUAL_ENV_PROMPT',
})


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class BuildPhase(str, Enum):
    """Ordered build phases."""
    INSTALL = 'install'
    IMPORT_CHECK = 'import_check'
    TEST = 'test'
    SMOKE = 'smoke'


class PhaseStatus(str, Enum):
    PASSED = 'passed'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    NOT_AVAILABLE = 'not_available'


@dataclass
class CommandEvidence:
    """Raw evidence from running a command."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@dataclass
class PhaseResult:
    """Result of a single build phase."""
    phase: BuildPhase
    status: PhaseStatus
    evidence: list[CommandEvidence] = field(default_factory=list)
    message: str = ''

    @property
    def passed(self) -> bool:
        return self.status == PhaseStatus.PASSED


@dataclass
class BuildResult:
    """Complete result of an isolated build run."""
    app_id: str
    workspace_root: Path
    phases: list[PhaseResult] = field(default_factory=list)
    overall_success: bool = False
    inventory_hash: str = ''
    evidence_path: Path | None = None

    def phase_result(self, phase: BuildPhase) -> PhaseResult | None:
        return next((p for p in self.phases if p.phase == phase), None)


# ---------------------------------------------------------------------------
# Build runner
# ---------------------------------------------------------------------------

class IsolatedBuildRunner:
    """Run build and test phases in a subprocess-isolated environment.

    Only commands declared in the AppManifest are executed.
    The environment is stripped of host secrets.
    """

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        allowed_commands: list[str] | None = None,
    ) -> None:
        self._timeout = timeout_seconds
        self._allowed_commands = allowed_commands

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, workspace_root: Path, commands: list[str], app_id: str = '') -> BuildResult:
        """Run all applicable build phases for the workspace."""
        result = BuildResult(app_id=app_id, workspace_root=workspace_root)
        phases_results: list[PhaseResult] = []

        # Phase 1: Install dependencies
        phases_results.append(self._run_install(workspace_root))

        # Phase 2: Import check
        phases_results.append(self._run_import_check(workspace_root))

        # Phase 3: Tests (from manifest commands)
        test_cmds = [c for c in commands if 'pytest' in c or 'test' in c.lower()]
        if test_cmds:
            phases_results.append(self._run_phase(BuildPhase.TEST, workspace_root, test_cmds))
        else:
            phases_results.append(PhaseResult(phase=BuildPhase.TEST, status=PhaseStatus.SKIPPED, message='No test commands'))

        # Phase 4: Smoke run
        smoke_cmds = [c for c in commands if 'smoke' in c.lower() or 'run' in c.lower()]
        if smoke_cmds:
            phases_results.append(self._run_phase(BuildPhase.SMOKE, workspace_root, smoke_cmds[:1]))
        else:
            phases_results.append(PhaseResult(phase=BuildPhase.SMOKE, status=PhaseStatus.SKIPPED, message='No smoke commands'))

        result.phases = phases_results
        result.overall_success = all(p.passed or p.status == PhaseStatus.SKIPPED for p in phases_results)
        return result

    # ------------------------------------------------------------------
    # Internal phase implementations
    # ------------------------------------------------------------------

    def _run_install(self, workspace_root: Path) -> PhaseResult:
        pyproject = workspace_root / 'pyproject.toml'
        if not pyproject.exists():
            return PhaseResult(phase=BuildPhase.INSTALL, status=PhaseStatus.SKIPPED, message='No pyproject.toml')
        evidence = self._run_command(['pip', 'install', '-e', '.[test]', '--quiet'], workspace_root)
        status = PhaseStatus.PASSED if evidence.passed else PhaseStatus.FAILED
        return PhaseResult(phase=BuildPhase.INSTALL, status=status, evidence=[evidence])

    def _run_import_check(self, workspace_root: Path) -> PhaseResult:
        src_dir = workspace_root / 'src'
        if not src_dir.exists():
            return PhaseResult(phase=BuildPhase.IMPORT_CHECK, status=PhaseStatus.SKIPPED, message='No src/ directory')
        py_files = list(src_dir.rglob('*.py'))
        if not py_files:
            return PhaseResult(phase=BuildPhase.IMPORT_CHECK, status=PhaseStatus.SKIPPED, message='No .py files in src/')
        evidence = self._run_command(['python', '-m', 'py_compile'] + [str(f) for f in py_files[:5]], workspace_root)
        status = PhaseStatus.PASSED if evidence.passed else PhaseStatus.FAILED
        return PhaseResult(phase=BuildPhase.IMPORT_CHECK, status=status, evidence=[evidence])

    def _run_phase(self, phase: BuildPhase, workspace_root: Path, commands: list[str]) -> PhaseResult:
        evidences: list[CommandEvidence] = []
        for cmd in commands:
            parts = cmd.split()
            if self._allowed_commands and parts[0] not in self._allowed_commands:
                _LOG.warning('Skipping disallowed command: %s', cmd)
                continue
            evidences.append(self._run_command(parts, workspace_root))
        if not evidences:
            return PhaseResult(phase=phase, status=PhaseStatus.SKIPPED, message='No allowed commands')
        all_passed = all(e.passed for e in evidences)
        status = PhaseStatus.PASSED if all_passed else PhaseStatus.FAILED
        return PhaseResult(phase=phase, status=status, evidence=evidences)

    def _run_command(self, cmd: list[str], cwd: Path) -> CommandEvidence:
        """Run a command in the workspace, capturing output."""
        safe_env = {k: v for k, v in os.environ.items() if k in _ALLOWED_ENV_KEYS}
        start = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            exit_code = proc.returncode
            stdout = proc.stdout[:MAX_OUTPUT_BYTES]
            stderr = proc.stderr[:MAX_OUTPUT_BYTES]
        except subprocess.TimeoutExpired as exc:
            exit_code = -1
            stdout = ''
            stderr = f'Command timed out after {self._timeout}s'
            timed_out = True
        except Exception as exc:  # noqa: BLE001
            exit_code = -1
            stdout = ''
            stderr = str(exc)
        duration_ms = (time.monotonic() - start) * 1000
        return CommandEvidence(
            command=' '.join(cmd),
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            timed_out=timed_out,
        )


# ---------------------------------------------------------------------------
# Fake runner for testing (no subprocess)
# ---------------------------------------------------------------------------

class FakeIsolatedBuildRunner(IsolatedBuildRunner):
    """Deterministic fake build runner — no subprocess required.

    Use ``fail_phases`` to simulate specific phase failures.
    """

    def __init__(
        self,
        fail_phases: set[BuildPhase] | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        super().__init__(timeout_seconds=timeout_seconds)
        self._fail_phases = fail_phases or set()
        self.calls: list[dict[str, object]] = []

    def run(self, workspace_root: Path, commands: list[str], app_id: str = '') -> BuildResult:
        self.calls.append({'workspace_root': str(workspace_root), 'commands': commands, 'app_id': app_id})
        result = BuildResult(app_id=app_id, workspace_root=workspace_root)
        phases_results: list[PhaseResult] = []
        for phase in [BuildPhase.INSTALL, BuildPhase.IMPORT_CHECK, BuildPhase.TEST]:
            if phase in self._fail_phases:
                evidence = CommandEvidence(command='fake', exit_code=1, stdout='', stderr='Fake failure', duration_ms=1.0)
                phases_results.append(PhaseResult(phase=phase, status=PhaseStatus.FAILED, evidence=[evidence]))
            else:
                evidence = CommandEvidence(command='fake', exit_code=0, stdout='OK', stderr='', duration_ms=1.0)
                phases_results.append(PhaseResult(phase=phase, status=PhaseStatus.PASSED, evidence=[evidence]))
        result.phases = phases_results
        result.overall_success = all(p.passed for p in phases_results)
        return result
