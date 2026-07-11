"""Tests for TASK-040: Execution Graph."""

from __future__ import annotations

import pytest

from workflow.graph import ExecutionGraph
from workflow.models import WorkflowDefinition, WorkflowStepDefinition


def _make_definition(steps: list[tuple[str, list[str], list[str]]]) -> WorkflowDefinition:
    """Helper — build a WorkflowDefinition from (name, inputs, outputs) tuples."""
    step_defs = [
        WorkflowStepDefinition(name=name, agent=name, inputs=inputs, outputs=outputs)
        for name, inputs, outputs in steps
    ]
    return WorkflowDefinition(name='test', version='1.0.0', steps=step_defs)


def test_nodes_in_definition_order() -> None:
    definition = _make_definition([('a', [], ['x']), ('b', ['x'], ['y']), ('c', ['y'], [])])
    graph = ExecutionGraph(definition)
    assert graph.nodes == ['a', 'b', 'c']


def test_predecessors_and_successors() -> None:
    definition = _make_definition([('a', [], ['x']), ('b', ['x'], [])])
    graph = ExecutionGraph(definition)
    assert graph.predecessors('b') == ['a']
    assert graph.successors('a') == ['b']
    assert graph.predecessors('a') == []
    assert graph.successors('b') == []


def test_topological_sort_linear() -> None:
    definition = _make_definition([('a', [], ['x']), ('b', ['x'], ['y']), ('c', ['y'], [])])
    graph = ExecutionGraph(definition)
    assert graph.topological_sort() == ['a', 'b', 'c']


def test_topological_sort_no_edges() -> None:
    definition = _make_definition([('a', [], []), ('b', [], []), ('c', [], [])])
    graph = ExecutionGraph(definition)
    order = graph.topological_sort()
    assert set(order) == {'a', 'b', 'c'}
    assert len(order) == 3


def test_parallel_stages_linear() -> None:
    definition = _make_definition([('a', [], ['x']), ('b', ['x'], ['y']), ('c', ['y'], [])])
    graph = ExecutionGraph(definition)
    stages = graph.parallel_stages()
    assert stages == [['a'], ['b'], ['c']]


def test_parallel_stages_fanout() -> None:
    definition = _make_definition([
        ('a', [], ['x']),
        ('b', ['x'], []),
        ('c', ['x'], []),
    ])
    graph = ExecutionGraph(definition)
    stages = graph.parallel_stages()
    assert stages[0] == ['a']
    assert sorted(stages[1]) == ['b', 'c']


def test_no_self_loop_edge() -> None:
    """A step that lists one of its own outputs as input should not create a self-loop."""
    definition = _make_definition([('a', ['x'], ['x'])])
    graph = ExecutionGraph(definition)
    assert graph.predecessors('a') == []
