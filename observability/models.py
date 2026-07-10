"""Observability models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Event:
    name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Metric:
    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Span:
    name: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LogEntry:
    level: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, Any] = field(default_factory=dict)
