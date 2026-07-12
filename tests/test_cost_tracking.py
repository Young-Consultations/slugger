"""Tests for TASK-053: LLM Cost Tracking."""

from __future__ import annotations

from observability.cost_tracker import CostTracker


def test_record_and_total_cost() -> None:
    tracker = CostTracker()
    record = tracker.record("openai", "gpt-4o", input_tokens=1000, output_tokens=500)
    # 1000/1000 * 0.005 + 500/1000 * 0.015 = 0.005 + 0.0075 = 0.0125
    assert abs(record.cost_usd - 0.0125) < 1e-6
    assert abs(tracker.total_cost() - 0.0125) < 1e-6


def test_zero_cost_for_mock() -> None:
    tracker = CostTracker()
    tracker.record("mock", "mock-model", input_tokens=5000, output_tokens=3000)
    assert tracker.total_cost() == 0.0


def test_cost_by_model() -> None:
    tracker = CostTracker()
    tracker.record("openai", "gpt-4o", input_tokens=1000, output_tokens=0)
    tracker.record("openai", "gpt-4o-mini", input_tokens=1000, output_tokens=0)
    by_model = tracker.cost_by_model()
    assert "openai/gpt-4o" in by_model
    assert "openai/gpt-4o-mini" in by_model


def test_cost_by_agent() -> None:
    tracker = CostTracker()
    tracker.record(
        "openai", "gpt-4o", input_tokens=1000, output_tokens=0, agent_name="req_agent"
    )
    tracker.record(
        "openai", "gpt-4o", input_tokens=500, output_tokens=0, agent_name="arch_agent"
    )
    by_agent = tracker.cost_by_agent()
    assert "req_agent" in by_agent
    assert "arch_agent" in by_agent


def test_total_tokens() -> None:
    tracker = CostTracker()
    tracker.record("mock", "mock-model", input_tokens=100, output_tokens=50)
    tracker.record("mock", "mock-model", input_tokens=200, output_tokens=75)
    totals = tracker.total_tokens()
    assert totals["input"] == 300
    assert totals["output"] == 125


def test_summary_structure() -> None:
    tracker = CostTracker()
    tracker.record("mock", "mock-model", input_tokens=10, output_tokens=5)
    summary = tracker.summary()
    assert "total_cost_usd" in summary
    assert "total_tokens" in summary
    assert "by_model" in summary
    assert "by_agent" in summary
    assert summary["record_count"] == 1


def test_unknown_model_zero_cost() -> None:
    tracker = CostTracker()
    record = tracker.record("custom", "my-llm", input_tokens=9999, output_tokens=9999)
    assert record.cost_usd == 0.0


def test_reset_clears_records() -> None:
    tracker = CostTracker()
    tracker.record("mock", "mock-model", input_tokens=100, output_tokens=50)
    tracker.reset()
    assert tracker.total_cost() == 0.0
    assert tracker.records() == []
