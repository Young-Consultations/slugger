"""Tests for TASK-054: Token Budgeting."""

from __future__ import annotations

import pytest

from observability.token_budget import (
    BudgetAllocation,
    BudgetExceededError,
    TokenBudget,
)


def test_consume_within_budget() -> None:
    budget = TokenBudget()
    budget.allocate(BudgetAllocation("run", max_total_tokens=10_000))
    usage = budget.consume("run", input_tokens=3_000, output_tokens=2_000)
    assert usage.total_tokens == 5_000


def test_remaining_with_limit() -> None:
    budget = TokenBudget()
    budget.allocate(BudgetAllocation("run", max_total_tokens=10_000))
    budget.consume("run", input_tokens=3_000, output_tokens=2_000)
    remaining = budget.remaining("run")
    assert remaining["total"] == 5_000


def test_remaining_no_limit_is_none() -> None:
    budget = TokenBudget()
    budget.allocate(BudgetAllocation("run"))
    budget.consume("run", input_tokens=100, output_tokens=50)
    remaining = budget.remaining("run")
    assert remaining["input"] is None
    assert remaining["output"] is None
    assert remaining["total"] is None


def test_strict_mode_raises_on_breach() -> None:
    budget = TokenBudget(strict=True)
    budget.allocate(BudgetAllocation("step", max_total_tokens=100))
    with pytest.raises(BudgetExceededError):
        budget.consume("step", input_tokens=101, output_tokens=0)


def test_non_strict_mode_records_overflow() -> None:
    budget = TokenBudget(strict=False)
    budget.allocate(BudgetAllocation("step", max_total_tokens=100))
    budget.consume("step", input_tokens=200, output_tokens=0)
    assert len(budget.overflows()) > 0


def test_consume_unregistered_scope_no_error() -> None:
    budget = TokenBudget()
    usage = budget.consume("unknown_scope", input_tokens=500, output_tokens=250)
    assert usage.total_tokens == 750


def test_summary() -> None:
    budget = TokenBudget()
    budget.allocate(BudgetAllocation("run"))
    budget.consume("run", input_tokens=100, output_tokens=50)
    summary = budget.summary()
    assert summary["total_input_tokens"] == 100
    assert summary["total_output_tokens"] == 50
