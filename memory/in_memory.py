"""In-memory memory backend."""

from __future__ import annotations

from memory.base import IMemoryBackend
from memory.models import MemoryEntry, MemoryQuery, MemoryResult


class InMemoryBackend(IMemoryBackend):
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], MemoryEntry] = {}

    def store(self, entry: MemoryEntry) -> MemoryEntry:
        self._entries[(entry.namespace, entry.key)] = entry
        return entry

    def retrieve(self, key: str, namespace: str = 'default') -> MemoryEntry | None:
        return self._entries.get((namespace, key))

    def search(self, query: MemoryQuery) -> MemoryResult:
        filtered = []
        for entry in self._entries.values():
            if query.namespace and entry.namespace != query.namespace:
                continue
            if query.text and query.text.lower() not in str(entry.value).lower() and query.text.lower() not in entry.key.lower():
                continue
            if query.tags and not set(query.tags).issubset(set(entry.tags)):
                continue
            filtered.append(entry)
        return MemoryResult(entries=filtered[: query.limit], total=len(filtered))

    def forget(self, key: str, namespace: str = 'default') -> None:
        self._entries.pop((namespace, key), None)
