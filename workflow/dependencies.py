"""Task dependency tracking for workflow steps.

:class:`TaskDependencyGraph` extends execution-graph concepts with named task
nodes that can have explicit string-level dependencies (not just inferred from
artifact I/O).  This is useful when defining ad-hoc pipeline configurations
outside of the YAML workflow engine.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class TaskNode:
    """A node in the task dependency graph.

    Parameters
    ----------
    name:
        Unique task name.
    description:
        Human-readable description.
    depends_on:
        Names of tasks that must complete before this task can start.
    metadata:
        Arbitrary key/value annotations.
    """

    name: str
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


class TaskDependencyGraph:
    """Directed dependency graph over :class:`TaskNode` objects.

    Tasks are registered with :meth:`add_task` and their declared
    ``depends_on`` lists are used to build edges.  Topological ordering and
    cycle detection are provided.

    Examples
    --------
    >>> g = TaskDependencyGraph()
    >>> g.add_task(TaskNode('lint'))
    >>> g.add_task(TaskNode('test', depends_on=['lint']))
    >>> g.add_task(TaskNode('deploy', depends_on=['test']))
    >>> g.topological_sort()
    ['lint', 'test', 'deploy']
    """

    def __init__(self) -> None:
        self._nodes: dict[str, TaskNode] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def add_task(self, task: TaskNode) -> None:
        """Register *task* in the graph.

        Raises
        ------
        ValueError
            If a task with the same name already exists.
        """
        if task.name in self._nodes:
            raise ValueError(f"Task '{task.name}' is already registered.")
        self._nodes[task.name] = task

    def get_task(self, name: str) -> TaskNode | None:
        """Return the :class:`TaskNode` for *name*, or ``None``."""
        return self._nodes.get(name)

    @property
    def tasks(self) -> list[TaskNode]:
        """All registered tasks (insertion order)."""
        return list(self._nodes.values())

    # ------------------------------------------------------------------
    # Graph queries
    # ------------------------------------------------------------------

    def dependencies_of(self, name: str) -> list[str]:
        """Return direct dependency names for task *name*."""
        task = self._nodes.get(name)
        return list(task.depends_on) if task else []

    def dependents_of(self, name: str) -> list[str]:
        """Return names of tasks that directly depend on *name*."""
        return [t.name for t in self._nodes.values() if name in t.depends_on]

    def topological_sort(self) -> list[str]:
        """Return tasks in a valid execution order.

        Raises
        ------
        ValueError
            If the graph contains a cycle.
        """
        in_degree: dict[str, int] = {name: 0 for name in self._nodes}
        adjacency: dict[str, list[str]] = {name: [] for name in self._nodes}

        for task in self._nodes.values():
            for dep in task.depends_on:
                if dep not in self._nodes:
                    raise ValueError(
                        f"Task '{task.name}' depends on unknown task '{dep}'."
                    )
                adjacency[dep].append(task.name)
                in_degree[task.name] += 1

        queue: deque[str] = deque(name for name, deg in in_degree.items() if deg == 0)
        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for successor in adjacency[node]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)

        if len(result) != len(self._nodes):
            raise ValueError("Task dependency graph contains a cycle.")
        return result

    def transitive_dependencies(self, name: str) -> set[str]:
        """Return the set of all (transitive) dependencies for task *name*."""
        visited: set[str] = set()
        queue: deque[str] = deque(self.dependencies_of(name))
        while queue:
            dep = queue.popleft()
            if dep not in visited:
                visited.add(dep)
                queue.extend(self.dependencies_of(dep))
        return visited
