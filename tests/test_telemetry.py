"""Tests for TASK-061: Telemetry."""

from __future__ import annotations

from observability.models import Event, Metric
from observability.telemetry import TelemetryCollector


def test_emit_and_retrieve_event() -> None:
    telemetry = TelemetryCollector()
    telemetry.emit_event(Event("workflow.started", payload={"run_id": "abc"}))
    events = telemetry.events()
    assert len(events) == 1
    assert events[0].name == "workflow.started"


def test_filter_events_by_prefix() -> None:
    telemetry = TelemetryCollector()
    telemetry.emit_event(Event("workflow.started"))
    telemetry.emit_event(Event("agent.execute.completed"))
    telemetry.emit_event(Event("workflow.finished"))
    workflow_events = telemetry.events(name_prefix="workflow.")
    assert len(workflow_events) == 2


def test_record_and_retrieve_metric() -> None:
    telemetry = TelemetryCollector()
    telemetry.record_metric(Metric("step.duration_ms", 42.0, tags={"step": "codegen"}))
    metrics = telemetry.metrics("step.duration_ms")
    assert len(metrics) == 1
    assert metrics[0].value == 42.0


def test_span_lifecycle() -> None:
    telemetry = TelemetryCollector()
    span = telemetry.start_span("execute_step", attributes={"step": "test"})
    assert span.ended_at is None
    telemetry.end_span(span)
    assert span.ended_at is not None


def test_export_structure() -> None:
    telemetry = TelemetryCollector()
    telemetry.emit_event(Event("test.event"))
    telemetry.record_metric(Metric("test.metric", 1.0))
    export = telemetry.export()
    assert len(export.events) == 1
    assert len(export.metrics) == 1
    assert export.events[0]["name"] == "test.event"


def test_export_to_json() -> None:
    telemetry = TelemetryCollector()
    telemetry.emit_event(Event("x"))
    json_str = telemetry.export().to_json()
    assert "exported_at" in json_str
    assert "x" in json_str


def test_max_events_drops_oldest() -> None:
    telemetry = TelemetryCollector(max_events=3)
    for i in range(5):
        telemetry.emit_event(Event(f"event.{i}"))
    events = telemetry.events()
    assert len(events) == 3
    assert events[0].name == "event.2"  # oldest three are 2, 3, 4


def test_reset_clears_all() -> None:
    telemetry = TelemetryCollector()
    telemetry.emit_event(Event("x"))
    telemetry.record_metric(Metric("y", 1.0))
    telemetry.reset()
    assert telemetry.events() == []
    assert telemetry.metrics() == []
