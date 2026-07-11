"""Agent memory — per-agent persistent context store.

:class:`AgentMemory` provides a namespaced view over a
:class:`~memory.memory_manager.MemoryManager` that is scoped to a single
agent.  It stores execution summaries, learned preferences, and intermediate
results that should persist across workflow runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from memory.memory_manager import MemoryManager
from memory.models import MemoryEntry, MemoryQuery


@dataclass
class AgentMemoryRecord:
    """A structured record stored in agent memory.

    Parameters
    ----------
    key:
        Unique key within the agent's namespace.
    content:
        The value to remember (any JSON-serialisable object).
    tags:
        Labels for filtering.
    importance:
        Numeric importance score (0–10).  Higher values are surfaced first
        when memory is compacted.
    """

    key: str
    content: Any
    tags: list[str] = field(default_factory=list)
    importance: float = 5.0


class AgentMemory:
    """Scoped memory interface for a single agent.

    All records are stored in a namespace derived from the agent name so they
    do not collide with other agents' memories.

    Parameters
    ----------
    agent_name:
        The canonical name of the owning agent.
    manager:
        Shared :class:`~memory.memory_manager.MemoryManager` instance.

    Examples
    --------
    >>> manager = MemoryManager(InMemoryBackend())
    >>> mem = AgentMemory('code_generator_agent', manager)
    >>> mem.remember('last_language', 'Python', tags=['prefs'])
    >>> mem.recall('last_language')
    'Python'
    """

    def __init__(self, agent_name: str, manager: MemoryManager) -> None:
        self._agent_name = agent_name
        self._manager = manager
        self._namespace = f'agent:{agent_name}'

    @property
    def agent_name(self) -> str:
        return self._agent_name

    # ------------------------------------------------------------------
    # Write API
    # ------------------------------------------------------------------

    def remember(
        self,
        key: str,
        content: Any,
        tags: list[str] | None = None,
        importance: float = 5.0,
    ) -> AgentMemoryRecord:
        """Persist *content* under *key* in the agent's namespace.

        Parameters
        ----------
        key:
            Storage key (unique within this agent).
        content:
            Value to store.
        tags:
            Optional labels.
        importance:
            Salience score.

        Returns
        -------
        AgentMemoryRecord
            The record that was stored.
        """
        record = AgentMemoryRecord(
            key=key,
            content=content,
            tags=tags or [],
            importance=importance,
        )
        self._manager.store(
            key,
            content,
            namespace=self._namespace,
            tags=(tags or []) + [f'importance:{importance}'],
        )
        return record

    def forget(self, key: str) -> None:
        """Remove *key* from the agent's namespace."""
        self._manager.forget(key, namespace=self._namespace)

    # ------------------------------------------------------------------
    # Read API
    # ------------------------------------------------------------------

    def recall(self, key: str) -> Any:
        """Return the stored value for *key*, or ``None``."""
        entry = self._manager.retrieve(key, namespace=self._namespace)
        return entry.value if entry is not None else None

    def search(self, text: str, limit: int = 10) -> list[MemoryEntry]:
        """Search memories by free-text query.

        Parameters
        ----------
        text:
            Query string.
        limit:
            Maximum number of results.

        Returns
        -------
        list[MemoryEntry]
        """
        result = self._manager.search(text, namespace=self._namespace)
        return result.entries[:limit]

    def all_entries(self) -> list[MemoryEntry]:
        """Return all entries in the agent's namespace."""
        result = self._manager.search('', namespace=self._namespace)
        return result.entries
