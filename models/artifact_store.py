"""In-memory artifact store."""

from __future__ import annotations

from collections.abc import Iterable

from models.artifact import Artifact


class InMemoryArtifactStore:
    """Simple test-only artifact store implementation backed by a dictionary."""

    TEST_ONLY = True

    def __init__(self) -> None:
        self._artifacts: dict[str, Artifact] = {}

    def create(self, artifact: Artifact) -> Artifact:
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def get(self, artifact_id: str) -> Artifact | None:
        return self._artifacts.get(artifact_id)

    def update(self, artifact: Artifact) -> Artifact:
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def delete(self, artifact_id: str) -> None:
        self._artifacts.pop(artifact_id, None)

    def list(self) -> list[Artifact]:
        return list(self._artifacts.values())

    def find_by_name(self, name: str) -> list[Artifact]:
        return [
            artifact for artifact in self._artifacts.values() if artifact.name == name
        ]

    def extend(self, artifacts: Iterable[Artifact]) -> None:
        for artifact in artifacts:
            self.create(artifact)
