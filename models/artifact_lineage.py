"""Artifact lineage model — track the SDLC traceability chain.

Provides :class:`ArtifactLineageNode` and :class:`LineageGraph` to record and
traverse the parent-child relationships between artifacts produced at each
stage of the AI-SDLC:

    Idea → Requirements → Stories → Architecture → ADR →
    Tasks → Code → Tests → Release

Each artifact can declare one or more *parent* artifact IDs so that the full
provenance of any artifact can be reconstructed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SdlcStage(str, Enum):
    """Standard SDLC stages used for lineage linking."""

    IDEA = 'idea'
    REQUIREMENTS = 'requirements'
    STORIES = 'stories'
    ARCHITECTURE = 'architecture'
    ADR = 'adr'
    TASKS = 'tasks'
    CODE = 'code'
    TESTS = 'tests'
    RELEASE = 'release'


@dataclass
class ArtifactLineageNode:
    """A single node in the artifact lineage graph.

    Parameters
    ----------
    artifact_id:
        Unique identifier of the artifact (matches :attr:`~models.artifact.Artifact.artifact_id`).
    name:
        Human-readable artifact name.
    stage:
        SDLC stage this artifact belongs to.
    parent_ids:
        IDs of artifacts this artifact was derived from.
    agent_name:
        Agent that produced this artifact.
    project_id:
        Project this artifact belongs to.
    created_at:
        UTC creation timestamp.
    metadata:
        Arbitrary extra traceability metadata.
    """

    artifact_id: str
    name: str
    stage: SdlcStage
    parent_ids: list[str] = field(default_factory=list)
    agent_name: str = 'unknown'
    project_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'artifact_id': self.artifact_id,
            'name': self.name,
            'stage': self.stage.value,
            'parent_ids': list(self.parent_ids),
            'agent_name': self.agent_name,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'metadata': dict(self.metadata),
        }


class LineageGraph:
    """Directed acyclic graph of artifact lineage relationships.

    Artifacts are added with :meth:`add` and lineage can be queried via
    :meth:`ancestors`, :meth:`descendants`, and :meth:`chain`.

    Examples
    --------
    >>> graph = LineageGraph()
    >>> req = ArtifactLineageNode('req-1', 'requirements', SdlcStage.REQUIREMENTS)
    >>> code = ArtifactLineageNode('code-1', 'generated_code', SdlcStage.CODE, parent_ids=['req-1'])
    >>> graph.add(req)
    >>> graph.add(code)
    >>> [n.stage for n in graph.ancestors('code-1')]
    [<SdlcStage.REQUIREMENTS: 'requirements'>]
    """

    def __init__(self) -> None:
        self._nodes: dict[str, ArtifactLineageNode] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, node: ArtifactLineageNode) -> None:
        """Register *node* in the graph."""
        self._nodes[node.artifact_id] = node

    def remove(self, artifact_id: str) -> None:
        """Remove a node from the graph (does not cascade to parent references)."""
        self._nodes.pop(artifact_id, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, artifact_id: str) -> ArtifactLineageNode | None:
        """Return the node with *artifact_id*, or ``None``."""
        return self._nodes.get(artifact_id)

    def ancestors(self, artifact_id: str) -> list[ArtifactLineageNode]:
        """Return all ancestor nodes of *artifact_id* (breadth-first).

        Returns an empty list if the artifact is not in the graph or has no
        parents.
        """
        node = self._nodes.get(artifact_id)
        if node is None:
            return []
        visited: set[str] = set()
        result: list[ArtifactLineageNode] = []
        queue = list(node.parent_ids)
        while queue:
            parent_id = queue.pop(0)
            if parent_id in visited:
                continue
            visited.add(parent_id)
            node = self._nodes.get(parent_id)
            if node is not None:
                result.append(node)
                queue.extend(p for p in node.parent_ids if p not in visited)
        return result

    def descendants(self, artifact_id: str) -> list[ArtifactLineageNode]:
        """Return all descendant nodes of *artifact_id* (breadth-first)."""
        visited: set[str] = set()
        result: list[ArtifactLineageNode] = []
        # Build a reverse index: parent_id → list of child IDs
        children: dict[str, list[str]] = {}
        for node in self._nodes.values():
            for parent_id in node.parent_ids:
                children.setdefault(parent_id, []).append(node.artifact_id)
        queue = list(children.get(artifact_id, []))
        while queue:
            child_id = queue.pop(0)
            if child_id in visited:
                continue
            visited.add(child_id)
            node = self._nodes.get(child_id)
            if node is not None:
                result.append(node)
                queue.extend(c for c in children.get(child_id, []) if c not in visited)
        return result

    def chain(self, artifact_id: str) -> list[ArtifactLineageNode]:
        """Return the full ancestor chain for *artifact_id*, ordered from root to *artifact_id*.

        The node for *artifact_id* is included as the last element.
        """
        ancestors = self.ancestors(artifact_id)
        # Sort ancestors by SdlcStage order
        stage_order = list(SdlcStage)
        ancestors_sorted = sorted(ancestors, key=lambda n: stage_order.index(n.stage) if n.stage in stage_order else 99)
        node = self._nodes.get(artifact_id)
        return ancestors_sorted + ([node] if node is not None else [])

    def nodes_by_stage(self, stage: SdlcStage) -> list[ArtifactLineageNode]:
        """Return all nodes at a given SDLC *stage*."""
        return [n for n in self._nodes.values() if n.stage == stage]

    def all_nodes(self) -> list[ArtifactLineageNode]:
        """Return all registered nodes."""
        return list(self._nodes.values())

    def to_dict(self) -> dict[str, Any]:
        """Serialise the graph to a JSON-compatible dictionary."""
        return {'nodes': [node.to_dict() for node in self._nodes.values()]}
