"""Observability reporting."""

from __future__ import annotations

from observability.collector import MetricsCollector
from observability.tracer import ExecutionTracer


class ObservabilityReporter:
    def __init__(self, collector: MetricsCollector, tracer: ExecutionTracer) -> None:
        self.collector = collector
        self.tracer = tracer

    def summarize(self) -> dict[str, int]:
        return {'metrics': len(self.collector.list()), 'spans': len(self.tracer.list())}
