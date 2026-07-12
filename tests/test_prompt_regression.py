"""Tests for TASK-052: Prompt Regression."""

from __future__ import annotations

from pathlib import Path

import pytest

from validators.prompt_evaluator import PromptEvaluator
from validators.prompt_regression import PromptRegressionSuite


def _setup_evaluator(tmp_path: Path) -> PromptEvaluator:
    """Create a PromptEvaluator with a simple template."""
    (tmp_path / "hello.md").write_text(
        "Hello, {{ name }}! Welcome to Slugger.", encoding="utf-8"
    )
    return PromptEvaluator(template_dir=tmp_path)


def test_capture_and_check_pass(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    suite = PromptRegressionSuite(evaluator)
    suite.capture_baseline("hello", {"name": "Alice"})
    result = suite.check("hello", {"name": "Alice"})
    assert result.passed


def test_check_fails_on_change(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    suite = PromptRegressionSuite(evaluator)
    suite.capture_baseline("hello", {"name": "Alice"})
    # Change the template
    (tmp_path / "hello.md").write_text(
        "Goodbye, {{ name }}! Bye Slugger.", encoding="utf-8"
    )
    result = suite.check("hello", {"name": "Alice"})
    assert not result.passed
    assert "mismatch" in result.message.lower()


def test_check_without_baseline_raises(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    suite = PromptRegressionSuite(evaluator)
    with pytest.raises(KeyError, match="hello"):
        suite.check("hello")


def test_run_all_returns_results(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    suite = PromptRegressionSuite(evaluator)
    suite.capture_baseline("hello", {"name": "Bob"})
    results = suite.run_all()
    assert len(results) == 1
    assert results[0].passed


def test_multiple_baselines_for_same_template_use_variables(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    suite = PromptRegressionSuite(evaluator)
    suite.capture_baseline("hello", {"name": "Alice"})
    suite.capture_baseline("hello", {"name": "Bob"})

    assert suite.check("hello", {"name": "Alice"}).passed
    assert suite.check("hello", {"name": "Bob"}).passed


def test_persistence(tmp_path) -> None:
    evaluator = _setup_evaluator(tmp_path)
    baseline_path = tmp_path / "baselines.json"
    suite = PromptRegressionSuite(evaluator, baseline_path=baseline_path)
    suite.capture_baseline("hello", {"name": "Carol"})
    assert baseline_path.exists()

    # Reload
    suite2 = PromptRegressionSuite(evaluator, baseline_path=baseline_path)
    result = suite2.check("hello", {"name": "Carol"})
    assert result.passed
