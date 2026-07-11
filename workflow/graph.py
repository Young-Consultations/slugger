"""Execution graph — dependency-aware DAG for workflow steps.

Each node in the graph is a step name.  Edges represent *data dependencies*:
if step B consumes an artifact produced by step A, there is an edge A→B.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from workflow.models import WorkflowDefinition


@dataclass
class ExecutionGraph:
    """Directed acyclic graph (DAG) derived from a :class:`WorkflowDefinition`.

    Nodes are step names.  Directed edges represent *must-run-before*
    relationships inferred from each step's ``inputs`` and ``outputs`` lists.

    Parameters
    ----------
    definition:
        The workflow definition to build the graph from.
    """

    definition: WorkflowDefinition
    _adjacency: dict[str, list[str]] = field(default_factory=dict, init=False, repr=False)
    _in_degree: dict[str, int] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> list[str]:
        """Return all step names in definition order."""
        return [step.name for step in self.definition.steps]

    def predecessors(self, step_name: str) -> list[str]:
        """Return names of steps that must complete before *step_name*."""
        return [
            src
            for src, targets in self._adjacency.items()
            if step_name in targets
        ]

    def successors(self, step_name: str) -> list[str]:
        """Return names of steps that depend on *step_name*."""
        return list(self._adjacency.get(step_name, []))

    def topological_sort(self) -> list[str]:
        """Return steps in a valid execution order (Kahn's algorithm).

        Raises
        ------
        ValueError
            If the graph contains a cycle.
        """
        in_degree = dict(self._in_degree)
        queue: deque[str] = deque(name for name, deg in in_degree.items() if deg == 0)
        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for successor in self._adjacency.get(node, []):
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)

        if len(result) != len(self.nodes):
            raise ValueError('Execution graph contains a cycle — cannot topologically sort.')
        return result

    def parallel_stages(self) -> list[list[str]]:
        """Group steps into parallel stages.

        Steps within the same stage have no dependencies on each other and
        can run concurrently.  Stages must be executed in order.

        Returns
        -------
        list[list[str]]
            Ordered list of stages, each stage being a list of step names.
        """
        in_degree = dict(self._in_degree)
        stages: list[list[str]] = []
        remaining = set(self.nodes)

        while remaining:
            ready = sorted(name for name in remaining if in_degree[name] == 0)
            if not ready:
                raise ValueError('Execution graph contains a cycle — cannot compute parallel stages.')
            stages.append(ready)
            for node in ready:
                remaining.discard(node)
                for successor in self._adjacency.get(node, []):
                    in_degree[successor] -= 1

        return stages

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build(self) -> None:
        """Build the adjacency list and in-degree map from step definitions."""
        # Map from artifact name → producing step name
        producers: dict[str, str] = {}
        for step in self.definition.steps:
            self._adjacency.setdefault(step.name, [])
            self._in_degree.setdefault(step.name, 0)
            for output in step.outputs:
                producers[output] = step.name

        for step in self.definition.steps:
            for artifact in step.inputs:
                producer = producers.get(artifact)
                if producer is not None and producer != step.name:
                    if step.name not in self._adjacency[producer]:
                        self._adjacency[producer].append(step.name)
                        self._in_degree[step.name] += 1
