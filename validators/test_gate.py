"""Mandatory-test gate — enforce that required test suites pass before a workflow step succeeds.

:class:`MandatoryTestGate` integrates with the quality-gate system:
it runs a declared set of test commands and fails the gate if any command
exits with a non-zero return code.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Outcome of a single test command run.

    Parameters
    ----------
    command:
        The command that was executed (as a list of strings).
    returncode:
        Process exit code.
    stdout:
        Captured standard output.
    stderr:
        Captured standard error.
    """

    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        """``True`` when the process exited with code 0."""
        return self.returncode == 0


@dataclass
class MandatoryTestGate:
    """Quality gate that mandates a set of test suites.

    Parameters
    ----------
    commands:
        List of shell command lists to run (e.g. ``[['pytest', 'tests/']]``).
    working_directory:
        Working directory for test execution.  Defaults to the current
        directory.
    timeout:
        Seconds to wait for each command before raising ``TimeoutExpired``.
    """

    commands: list[list[str]] = field(default_factory=list)
    working_directory: Path = field(default_factory=Path)
    timeout: float = 120.0

    def add_command(self, command: list[str]) -> None:
        """Register an additional test *command*."""
        self.commands.append(command)

    def run(self) -> list[TestResult]:
        """Execute all registered commands and return their results.

        Returns
        -------
        list[TestResult]
            One result per registered command, in declaration order.
        """
        results: list[TestResult] = []
        for cmd in self.commands:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_directory,
            )
            results.append(
                TestResult(
                    command=cmd,
                    returncode=proc.returncode,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                )
            )
        return results

    def evaluate(self) -> dict[str, Any]:
        """Run all commands and return a summary dict.

        The summary contains:

        * ``passed`` (bool) — ``True`` iff all commands succeeded.
        * ``results`` — list of per-command result dicts.
        * ``failures`` — list of failing command strings.
        """
        results = self.run()
        failures = [' '.join(r.command) for r in results if not r.passed]
        return {
            'passed': len(failures) == 0,
            'results': [
                {
                    'command': ' '.join(r.command),
                    'returncode': r.returncode,
                    'passed': r.passed,
                }
                for r in results
            ],
            'failures': failures,
        }
