"""Tests for TASK-045: Task Dependencies."""

from __future__ import annotations

import pytest

from workflow.dependencies import TaskDependencyGraph, TaskNode


def test_topological_sort_linear() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("lint"))
    g.add_task(TaskNode("test", depends_on=["lint"]))
    g.add_task(TaskNode("deploy", depends_on=["test"]))
    assert g.topological_sort() == ["lint", "test", "deploy"]


def test_topological_sort_no_deps() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("a"))
    g.add_task(TaskNode("b"))
    order = g.topological_sort()
    assert set(order) == {"a", "b"}


def test_cycle_raises() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("a", depends_on=["b"]))
    g.add_task(TaskNode("b", depends_on=["a"]))
    with pytest.raises(ValueError, match="cycle"):
        g.topological_sort()


def test_unknown_dependency_raises() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("a", depends_on=["ghost"]))
    with pytest.raises(ValueError, match="unknown task"):
        g.topological_sort()


def test_duplicate_task_raises() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("a"))
    with pytest.raises(ValueError, match="already registered"):
        g.add_task(TaskNode("a"))


def test_dependencies_of() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("lint"))
    g.add_task(TaskNode("test", depends_on=["lint"]))
    assert g.dependencies_of("test") == ["lint"]
    assert g.dependencies_of("lint") == []


def test_dependents_of() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("lint"))
    g.add_task(TaskNode("test", depends_on=["lint"]))
    assert g.dependents_of("lint") == ["test"]
    assert g.dependents_of("test") == []


def test_transitive_dependencies() -> None:
    g = TaskDependencyGraph()
    g.add_task(TaskNode("a"))
    g.add_task(TaskNode("b", depends_on=["a"]))
    g.add_task(TaskNode("c", depends_on=["b"]))
    assert g.transitive_dependencies("c") == {"a", "b"}
    assert g.transitive_dependencies("b") == {"a"}
    assert g.transitive_dependencies("a") == set()
