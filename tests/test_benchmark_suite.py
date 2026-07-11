"""Tests for TASK-062: Benchmark Suite."""

from __future__ import annotations

import time

import pytest

from benchmarks.suite import BenchmarkSuite, BudgetSpec


def test_run_single_benchmark() -> None:
    suite = BenchmarkSuite(iterations=5)
    suite.register('noop', lambda: None)
    result = suite.run('noop')
    assert result.passed
    assert result.iterations == 5
    assert result.elapsed_ms >= 0
    assert result.avg_ms >= 0


def test_run_all_returns_all() -> None:
    suite = BenchmarkSuite(iterations=2)
    suite.register('a', lambda: None)
    suite.register('b', lambda: None)
    results = suite.run_all()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {'a', 'b'}


def test_error_captured() -> None:
    suite = BenchmarkSuite(iterations=1)
    suite.register('failing', lambda: 1 / 0)
    result = suite.run('failing')
    assert not result.passed
    assert 'division by zero' in result.error.lower()


def test_unknown_name_raises() -> None:
    suite = BenchmarkSuite()
    with pytest.raises(KeyError):
        suite.run('nonexistent')


def test_budget_pass() -> None:
    suite = BenchmarkSuite(iterations=1)
    suite.register('fast', lambda: None)
    suite.set_budget(BudgetSpec('fast', max_avg_ms=1000.0))
    results = suite.run_all()
    check = suite.check_budgets(results)
    assert check['passed']


def test_budget_fail() -> None:
    suite = BenchmarkSuite(iterations=1)
    suite.register('slow', lambda: time.sleep(0.05))
    suite.set_budget(BudgetSpec('slow', max_avg_ms=1.0))  # 1ms budget — will fail
    results = suite.run_all()
    check = suite.check_budgets(results)
    assert not check['passed']
    assert len(check['violations']) == 1


def test_custom_iteration_count() -> None:
    suite = BenchmarkSuite(iterations=10)
    suite.register('custom', lambda: None, iterations=3)
    result = suite.run('custom')
    assert result.iterations == 3
