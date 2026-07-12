"""Memory backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from memory.models import MemoryEntry, MemoryQuery, MemoryResult


class IMemoryBackend(ABC):
    @abstractmethod
    def store(self, entry: MemoryEntry) -> MemoryEntry:
        """Persist a memory entry."""

    @abstractmethod
    def retrieve(self, key: str, namespace: str = "default") -> MemoryEntry | None:
        """Retrieve a memory entry."""

    @abstractmethod
    def search(self, query: MemoryQuery) -> MemoryResult:
        """Search stored memories."""

    @abstractmethod
    def forget(self, key: str, namespace: str = "default") -> None:
        """Delete a memory entry."""
