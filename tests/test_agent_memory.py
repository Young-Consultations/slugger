"""Tests for TASK-051: Agent Memory."""

from __future__ import annotations

from memory import InMemoryBackend, MemoryManager
from memory.agent_memory import AgentMemory


def _make_agent_memory(agent_name: str = 'test_agent') -> AgentMemory:
    manager = MemoryManager(InMemoryBackend())
    return AgentMemory(agent_name, manager)


def test_remember_and_recall() -> None:
    mem = _make_agent_memory()
    mem.remember('preferred_lang', 'Python')
    assert mem.recall('preferred_lang') == 'Python'


def test_recall_missing_returns_none() -> None:
    mem = _make_agent_memory()
    assert mem.recall('nonexistent') is None


def test_forget() -> None:
    mem = _make_agent_memory()
    mem.remember('key', 'val')
    mem.forget('key')
    assert mem.recall('key') is None


def test_search() -> None:
    mem = _make_agent_memory()
    mem.remember('arch', 'microservices pattern', tags=['architecture'])
    results = mem.search('microservices')
    assert len(results) > 0


def test_agent_namespaces_are_isolated() -> None:
    manager = MemoryManager(InMemoryBackend())
    mem_a = AgentMemory('agent_a', manager)
    mem_b = AgentMemory('agent_b', manager)
    mem_a.remember('color', 'blue')
    assert mem_b.recall('color') is None


def test_agent_name_property() -> None:
    mem = _make_agent_memory('my_agent')
    assert mem.agent_name == 'my_agent'


def test_all_entries_returns_records() -> None:
    mem = _make_agent_memory()
    mem.remember('a', 1)
    mem.remember('b', 2)
    entries = mem.all_entries()
    assert len(entries) >= 2
