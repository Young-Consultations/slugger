"""Tests for Epic 8: observability dashboard and failure analytics."""

from __future__ import annotations

import pytest

from observability.collector import MetricsCollector
from observability.dashboard import (
    DashboardSnapshot,
    FailureAnalytics,
    MetricsDashboard,
)
from observability.tracer import ExecutionTracer


@pytest.fixture()
def analytics() -> FailureAnalytics:
    return FailureAnalytics()


@pytest.fixture()
def dashboard() -> MetricsDashboard:
    collector = MetricsCollector()
    tracer = ExecutionTracer()
    analytics = FailureAnalytics()
    return MetricsDashboard(collector, tracer, analytics)


# ---------------------------------------------------------------------------
# FailureAnalytics
# ---------------------------------------------------------------------------


def test_record_failure(analytics: FailureAnalytics) -> None:
    record = analytics.record(
        "generate_code", "code_generator_agent", "timeout", "Request timed out"
    )
    assert record.step_name == "generate_code"
    assert record.error_type == "timeout"


def test_failures_filter_by_agent(analytics: FailureAnalytics) -> None:
    analytics.record("step1", "agent_a", "error", "err")
    analytics.record("step2", "agent_b", "error", "err")
    assert len(analytics.failures(agent_name="agent_a")) == 1


def test_failures_filter_by_type(analytics: FailureAnalytics) -> None:
    analytics.record("step1", "agent_a", "timeout", "err")
    analytics.record("step2", "agent_a", "validation", "err")
    assert len(analytics.failures(error_type="timeout")) == 1


def test_top_failing_agents(analytics: FailureAnalytics) -> None:
    analytics.record("s1", "agent_a", "err", "e")
    analytics.record("s2", "agent_a", "err", "e")
    analytics.record("s3", "agent_b", "err", "e")
    top = analytics.top_failing_agents(limit=2)
    assert top[0][0] == "agent_a"
    assert top[0][1] == 2


def test_failure_summary(analytics: FailureAnalytics) -> None:
    analytics.record("s1", "a", "timeout", "e")
    analytics.record("s2", "a", "timeout", "e")
    analytics.record("s3", "b", "validation", "e")
    summary = analytics.summary()
    assert summary["total_failures"] == 3
    assert summary["by_error_type"]["timeout"] == 2
    assert summary["by_agent"]["a"] == 2


def test_failure_record_to_dict(analytics: FailureAnalytics) -> None:
    record = analytics.record("step", "agent", "error", "message")
    data = record.to_dict()
    assert data["step_name"] == "step"
    assert data["error_type"] == "error"
    assert "timestamp" in data


# ---------------------------------------------------------------------------
# MetricsDashboard
# ---------------------------------------------------------------------------


def test_dashboard_snapshot_empty(dashboard: MetricsDashboard) -> None:
    snapshot = dashboard.snapshot()
    assert isinstance(snapshot, DashboardSnapshot)
    assert snapshot.metrics_summary["total_metrics"] == 0
    assert snapshot.span_summary["total_spans"] == 0
    assert snapshot.failure_summary["total_failures"] == 0


def test_dashboard_record_metric(dashboard: MetricsDashboard) -> None:
    metric = dashboard.record_metric("agent.latency", 1.23, agent="code_generator")
    assert metric.name == "agent.latency"
    assert metric.value == 1.23
    assert metric.tags == {"agent": "code_generator"}


def test_dashboard_snapshot_with_metrics(dashboard: MetricsDashboard) -> None:
    dashboard.record_metric("latency", 1.0)
    dashboard.record_metric("latency", 2.0)
    snapshot = dashboard.snapshot()
    assert snapshot.metrics_summary["total_metrics"] == 2
    by_name = snapshot.metrics_summary["by_name"]["latency"]
    assert by_name["count"] == 2
    assert by_name["min"] == 1.0
    assert by_name["max"] == 2.0
    assert by_name["avg"] == 1.5


def test_dashboard_snapshot_includes_failure_summary(
    dashboard: MetricsDashboard,
) -> None:
    dashboard.analytics.record("step", "agent", "error", "msg")
    snapshot = dashboard.snapshot()
    assert snapshot.failure_summary["total_failures"] == 1


def test_dashboard_snapshot_to_dict(dashboard: MetricsDashboard) -> None:
    snapshot = dashboard.snapshot()
    data = snapshot.to_dict()
    assert "generated_at" in data
    assert "metrics" in data
    assert "spans" in data
    assert "failures" in data
    assert "tokens" in data


def test_dashboard_span_timing(dashboard: MetricsDashboard) -> None:
    from datetime import timedelta

    span = dashboard.tracer.start_span("test-span")
    # Simulate the span ending 0.5 seconds later
    span.ended_at = span.started_at + timedelta(seconds=0.5)
    snapshot = dashboard.snapshot()
    assert snapshot.span_summary["completed_spans"] == 1
    assert snapshot.span_summary["avg_duration_seconds"] == pytest.approx(0.5, abs=0.01)
