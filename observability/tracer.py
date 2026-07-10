"""Execution tracer."""

from __future__ import annotations

from datetime import datetime, timezone

from observability.models import Span


class ExecutionTracer:
    def __init__(self) -> None:
        self._spans: list[Span] = []

    def start_span(self, name: str, **attributes: object) -> Span:
        span = Span(name=name, attributes=dict(attributes))
        self._spans.append(span)
        return span

    def end_span(self, span: Span) -> None:
        span.ended_at = datetime.now(timezone.utc)

    def list(self) -> list[Span]:
        return list(self._spans)
