"""Structured JSON logger."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from observability.models import LogEntry


class StructuredLogger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str, **context: object) -> LogEntry:
        entry = LogEntry(level=level, message=message, context=dict(context))
        payload = asdict(entry)
        payload['timestamp'] = entry.timestamp.isoformat()
        with self.path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload) + '\n')
        return entry
