"""Telemetry — structured event emission for runtime observability.

:class:`TelemetryCollector` captures events, metrics, and spans from across
the Slugger runtime in a single, queryable store.  It bridges the observability
subsystem with external exporters (structured logs, Prometheus, OTLP, …).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from observability.models import Event, Metric, Span


@dataclass
class TelemetryExport:
    """A point-in-time snapshot exported by the telemetry system."""

    exported_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    events: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    spans: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exported_at": self.exported_at.isoformat(),
            "events": self.events,
            "metrics": self.metrics,
            "spans": self.spans,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class TelemetryCollector:
    """Accumulate telemetry signals and export them on demand.

    Parameters
    ----------
    max_events:
        Maximum number of events to buffer before the oldest are dropped.
        ``None`` means unlimited.

    Examples
    --------
    >>> telemetry = TelemetryCollector()
    >>> telemetry.emit_event(Event('workflow.started', payload={'run_id': 'abc'}))
    >>> telemetry.record_metric(Metric('step.duration_ms', 42.0))
    >>> export = telemetry.export()
    >>> export.events[0]['name']
    'workflow.started'
    """

    def __init__(self, max_events: int | None = 10_000) -> None:
        self._max_events = max_events
        self._events: list[Event] = []
        self._metrics: list[Metric] = []
        self._spans: list[Span] = []

    # ------------------------------------------------------------------
    # Signal ingestion
    # ------------------------------------------------------------------

    def emit_event(self, event: Event) -> None:
        """Record a structured event."""
        self._events.append(event)
        if self._max_events is not None and len(self._events) > self._max_events:
            self._events.pop(0)

    def record_metric(self, metric: Metric) -> None:
        """Record a metric observation."""
        self._metrics.append(metric)

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        """Open a new span and add it to the buffer.

        Returns
        -------
        Span
            The open span (``ended_at`` is still ``None``).
        """
        span = Span(name=name, attributes=attributes or {})
        self._spans.append(span)
        return span

    def end_span(self, span: Span) -> None:
        """Close *span* by recording its end time."""
        span.ended_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def events(self, name_prefix: str | None = None) -> list[Event]:
        """Return recorded events, optionally filtered by name prefix."""
        if name_prefix is None:
            return list(self._events)
        return [e for e in self._events if e.name.startswith(name_prefix)]

    def metrics(self, name: str | None = None) -> list[Metric]:
        """Return recorded metrics, optionally filtered by exact name."""
        if name is None:
            return list(self._metrics)
        return [m for m in self._metrics if m.name == name]

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self) -> TelemetryExport:
        """Snapshot current telemetry data into a :class:`TelemetryExport`."""

        def _event_dict(e: Event) -> dict[str, Any]:
            return {
                "name": e.name,
                "timestamp": e.timestamp.isoformat(),
                "payload": e.payload,
            }

        def _metric_dict(m: Metric) -> dict[str, Any]:
            return {"name": m.name, "value": m.value, "tags": m.tags}

        def _span_dict(s: Span) -> dict[str, Any]:
            return {
                "name": s.name,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "duration_ms": (
                    (s.ended_at - s.started_at).total_seconds() * 1000
                    if s.ended_at
                    else None
                ),
                "attributes": s.attributes,
            }

        return TelemetryExport(
            events=[_event_dict(e) for e in self._events],
            metrics=[_metric_dict(m) for m in self._metrics],
            spans=[_span_dict(s) for s in self._spans],
        )

    def reset(self) -> None:
        """Clear all buffered telemetry data."""
        self._events.clear()
        self._metrics.clear()
        self._spans.clear()
