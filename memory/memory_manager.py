"""Memory manager facade."""

from __future__ import annotations

from typing import Any

from memory.base import IMemoryBackend
from memory.models import MemoryEntry, MemoryQuery, MemoryResult


class MemoryManager:
    def __init__(self, backend: IMemoryBackend) -> None:
        self.backend = backend

    def store(self, key: str, value: Any, namespace: str = 'default', tags: list[str] | None = None) -> MemoryEntry:
        return self.backend.store(MemoryEntry(key=key, value=value, namespace=namespace, tags=tags or []))

    def retrieve(self, key: str, namespace: str = 'default') -> MemoryEntry | None:
        return self.backend.retrieve(key, namespace)

    def search(self, text: str = '', namespace: str | None = None, tags: list[str] | None = None, limit: int = 10) -> MemoryResult:
        return self.backend.search(MemoryQuery(text=text, namespace=namespace, tags=tags or [], limit=limit))

    def forget(self, key: str, namespace: str = 'default') -> None:
        self.backend.forget(key, namespace)
