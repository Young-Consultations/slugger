"""Metrics collector."""

from __future__ import annotations

from observability.models import Metric


class MetricsCollector:
    def __init__(self) -> None:
        self._metrics: list[Metric] = []

    def record(self, metric: Metric) -> None:
        self._metrics.append(metric)

    def list(self) -> list[Metric]:
        return list(self._metrics)
