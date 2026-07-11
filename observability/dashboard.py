"""Observability metrics dashboard and failure analytics.

:class:`MetricsDashboard` aggregates metrics, spans, and failure events
into a unified dashboard view.  :class:`FailureAnalytics` provides
categorised failure analysis and trend reporting.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from observability.collector import MetricsCollector
from observability.models import Metric, Span
from observability.tracer import ExecutionTracer


# ---------------------------------------------------------------------------
# Failure Analytics
# ---------------------------------------------------------------------------


@dataclass
class FailureRecord:
    """A single recorded failure event.

    Parameters
    ----------
    step_name:
        Workflow step where the failure occurred.
    agent_name:
        Name of the agent that failed.
    error_type:
        Short classification of the error (e.g. ``'timeout'``, ``'validation'``).
    message:
        Full error message.
    timestamp:
        UTC time of occurrence.
    metadata:
        Arbitrary extra context.
    """

    step_name: str
    agent_name: str
    error_type: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'step_name': self.step_name,
            'agent_name': self.agent_name,
            'error_type': self.error_type,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': dict(self.metadata),
        }


class FailureAnalytics:
    """Record and analyse workflow failure events.

    Examples
    --------
    >>> analytics = FailureAnalytics()
    >>> analytics.record('generate_code', 'code_generator_agent', 'timeout', 'Request timed out')
    >>> analytics.summary()
    {'total_failures': 1, 'by_error_type': {'timeout': 1}, 'by_agent': {'code_generator_agent': 1}}
    """

    def __init__(self) -> None:
        self._failures: list[FailureRecord] = []

    def record(
        self,
        step_name: str,
        agent_name: str,
        error_type: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> FailureRecord:
        """Record a new failure event and return the record."""
        record = FailureRecord(
            step_name=step_name,
            agent_name=agent_name,
            error_type=error_type,
            message=message,
            metadata=metadata or {},
        )
        self._failures.append(record)
        return record

    def failures(
        self,
        *,
        step_name: str | None = None,
        agent_name: str | None = None,
        error_type: str | None = None,
    ) -> list[FailureRecord]:
        """Return failure records, optionally filtered."""
        result = self._failures
        if step_name is not None:
            result = [f for f in result if f.step_name == step_name]
        if agent_name is not None:
            result = [f for f in result if f.agent_name == agent_name]
        if error_type is not None:
            result = [f for f in result if f.error_type == error_type]
        return list(result)

    def top_failing_agents(self, limit: int = 5) -> list[tuple[str, int]]:
        """Return the agents with the most failures, sorted descending."""
        counts: dict[str, int] = defaultdict(int)
        for f in self._failures:
            counts[f.agent_name] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def summary(self) -> dict[str, Any]:
        """Return a summary of failure analytics."""
        by_type: dict[str, int] = defaultdict(int)
        by_agent: dict[str, int] = defaultdict(int)
        by_step: dict[str, int] = defaultdict(int)
        for f in self._failures:
            by_type[f.error_type] += 1
            by_agent[f.agent_name] += 1
            by_step[f.step_name] += 1
        return {
            'total_failures': len(self._failures),
            'by_error_type': dict(by_type),
            'by_agent': dict(by_agent),
            'by_step': dict(by_step),
        }


# ---------------------------------------------------------------------------
# Metrics Dashboard
# ---------------------------------------------------------------------------


@dataclass
class DashboardSnapshot:
    """Point-in-time snapshot of the observability dashboard.

    Parameters
    ----------
    generated_at:
        UTC time the snapshot was created.
    metrics_summary:
        Aggregated metrics statistics.
    span_summary:
        Execution timing summary from spans.
    failure_summary:
        Failure analytics summary.
    token_summary:
        Optional LLM token/cost summary if a cost tracker is available.
    """

    generated_at: datetime
    metrics_summary: dict[str, Any]
    span_summary: dict[str, Any]
    failure_summary: dict[str, Any]
    token_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'generated_at': self.generated_at.isoformat(),
            'metrics': self.metrics_summary,
            'spans': self.span_summary,
            'failures': self.failure_summary,
            'tokens': self.token_summary,
        }


class MetricsDashboard:
    """Aggregates observability data from multiple sources into a dashboard.

    Parameters
    ----------
    collector:
        :class:`~observability.collector.MetricsCollector` instance.
    tracer:
        :class:`~observability.tracer.ExecutionTracer` instance.
    analytics:
        :class:`FailureAnalytics` instance.
    cost_tracker:
        Optional :class:`~observability.cost_tracker.CostTracker` instance.
        When supplied, token and cost data are included in the snapshot.

    Examples
    --------
    >>> dashboard = MetricsDashboard(collector, tracer, analytics)
    >>> snapshot = dashboard.snapshot()
    >>> snapshot.metrics_summary['total_metrics']
    3
    """

    def __init__(
        self,
        collector: MetricsCollector,
        tracer: ExecutionTracer,
        analytics: FailureAnalytics,
        cost_tracker: Any | None = None,
    ) -> None:
        self.collector = collector
        self.tracer = tracer
        self.analytics = analytics
        self.cost_tracker = cost_tracker

    def snapshot(self) -> DashboardSnapshot:
        """Generate a point-in-time dashboard snapshot."""
        metrics = self.collector.list()
        spans = self.tracer.list()

        # Metrics summary
        metric_names: dict[str, list[float]] = defaultdict(list)
        for m in metrics:
            metric_names[m.name].append(m.value)
        metrics_summary: dict[str, Any] = {
            'total_metrics': len(metrics),
            'unique_names': len(metric_names),
            'by_name': {
                name: {
                    'count': len(vals),
                    'min': min(vals),
                    'max': max(vals),
                    'avg': round(sum(vals) / len(vals), 4),
                }
                for name, vals in metric_names.items()
            },
        }

        # Span summary
        completed = [s for s in spans if s.ended_at is not None]
        durations = [
            (s.ended_at - s.started_at).total_seconds()
            for s in completed
            if s.ended_at is not None
        ]
        span_summary: dict[str, Any] = {
            'total_spans': len(spans),
            'completed_spans': len(completed),
            'avg_duration_seconds': round(sum(durations) / len(durations), 4) if durations else 0.0,
            'max_duration_seconds': round(max(durations), 4) if durations else 0.0,
            'min_duration_seconds': round(min(durations), 4) if durations else 0.0,
        }

        # Token / cost summary
        token_summary: dict[str, Any] = {}
        if self.cost_tracker is not None:
            token_summary = self.cost_tracker.summary()

        return DashboardSnapshot(
            generated_at=datetime.now(timezone.utc),
            metrics_summary=metrics_summary,
            span_summary=span_summary,
            failure_summary=self.analytics.summary(),
            token_summary=token_summary,
        )

    def record_metric(self, name: str, value: float, **tags: str) -> Metric:
        """Record a single metric and return it."""
        metric = Metric(name=name, value=value, tags=dict(tags))
        self.collector.record(metric)
        return metric
