"""Tests for TASK-047: Mandatory Tests."""

from __future__ import annotations

import sys

from validators.test_gate import MandatoryTestGate, TestResult


def test_passing_command() -> None:
    gate = MandatoryTestGate(commands=[[sys.executable, "-c", "exit(0)"]])
    results = gate.run()
    assert len(results) == 1
    assert results[0].passed


def test_failing_command() -> None:
    gate = MandatoryTestGate(commands=[[sys.executable, "-c", "exit(1)"]])
    results = gate.run()
    assert len(results) == 1
    assert not results[0].passed
    assert results[0].returncode == 1


def test_evaluate_all_pass() -> None:
    gate = MandatoryTestGate(
        commands=[
            [sys.executable, "-c", "exit(0)"],
            [sys.executable, "-c", "exit(0)"],
        ]
    )
    summary = gate.evaluate()
    assert summary["passed"] is True
    assert summary["failures"] == []


def test_evaluate_partial_failure() -> None:
    gate = MandatoryTestGate(
        commands=[
            [sys.executable, "-c", "exit(0)"],
            [sys.executable, "-c", "exit(2)"],
        ]
    )
    summary = gate.evaluate()
    assert summary["passed"] is False
    assert len(summary["failures"]) == 1


def test_add_command() -> None:
    gate = MandatoryTestGate()
    gate.add_command([sys.executable, "-c", "exit(0)"])
    results = gate.run()
    assert results[0].passed


def test_test_result_properties() -> None:
    result = TestResult(command=["echo"], returncode=0, stdout="ok", stderr="")
    assert result.passed
    bad = TestResult(command=["fail"], returncode=1, stdout="", stderr="error")
    assert not bad.passed
