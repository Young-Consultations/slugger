"""File-backed memory backend."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from memory.base import IMemoryBackend
from memory.models import MemoryEntry, MemoryQuery, MemoryResult


class FileMemoryBackend(IMemoryBackend):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text('[]', encoding='utf-8')

    def store(self, entry: MemoryEntry) -> MemoryEntry:
        entries = self._load()
        entries[(entry.namespace, entry.key)] = entry
        self._save(entries)
        return entry

    def retrieve(self, key: str, namespace: str = 'default') -> MemoryEntry | None:
        return self._load().get((namespace, key))

    def search(self, query: MemoryQuery) -> MemoryResult:
        filtered = []
        for entry in self._load().values():
            if query.namespace and entry.namespace != query.namespace:
                continue
            if query.text and query.text.lower() not in str(entry.value).lower() and query.text.lower() not in entry.key.lower():
                continue
            if query.tags and not set(query.tags).issubset(set(entry.tags)):
                continue
            filtered.append(entry)
        return MemoryResult(entries=filtered[: query.limit], total=len(filtered))

    def forget(self, key: str, namespace: str = 'default') -> None:
        entries = self._load()
        entries.pop((namespace, key), None)
        self._save(entries)

    def _load(self) -> dict[tuple[str, str], MemoryEntry]:
        raw_entries = json.loads(self.path.read_text(encoding='utf-8'))
        result: dict[tuple[str, str], MemoryEntry] = {}
        for item in raw_entries:
            result[(item['namespace'], item['key'])] = MemoryEntry(
                key=item['key'], value=item['value'], namespace=item['namespace'], tags=item.get('tags', []),
                created_at=datetime.fromisoformat(item['created_at']), updated_at=datetime.fromisoformat(item['updated_at'])
            )
        return result

    def _save(self, entries: dict[tuple[str, str], MemoryEntry]) -> None:
        serializable = []
        for entry in entries.values():
            payload = asdict(entry)
            payload['created_at'] = entry.created_at.isoformat()
            payload['updated_at'] = entry.updated_at.isoformat()
            serializable.append(payload)
        self.path.write_text(json.dumps(serializable, indent=2), encoding='utf-8')
