"""Memory models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class MemoryEntry:
    key: str
    value: Any
    namespace: str = "default"
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class MemoryQuery:
    text: str = ""
    namespace: str | None = None
    tags: list[str] = field(default_factory=list)
    limit: int = 10


@dataclass(slots=True)
class MemoryResult:
    entries: list[MemoryEntry] = field(default_factory=list)
    total: int = 0
