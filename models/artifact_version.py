"""Artifact versioning — track the history of each named artifact.

:class:`ArtifactVersionStore` wraps an
:class:`~models.artifact_store.InMemoryArtifactStore` and maintains an ordered
version history per artifact name.  Every time a new version of an artifact is
stored the version string on its
:class:`~models.artifact.ArtifactMetadata` is bumped automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from models.artifact import Artifact


@dataclass
class ArtifactVersion:
    """A single entry in the version history of an artifact."""

    artifact_id: str
    name: str
    version: str
    content: str
    metadata_snapshot: dict[str, Any] = field(default_factory=dict)


def _bump_version(current: str) -> str:
    """Increment the *patch* component of a SemVer version string.

    Examples
    --------
    >>> _bump_version('1.0.0')
    '1.0.1'
    >>> _bump_version('2.3.9')
    '2.3.10'
    """
    parts = current.split('.')
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except (ValueError, IndexError):
        parts.append('1')
    return '.'.join(parts)


class ArtifactVersionStore:
    """Maintain an ordered version history for each named artifact.

    Parameters
    ----------
    None
        The store is initialised empty; artifacts are added via
        :meth:`store`.

    Examples
    --------
    >>> store = ArtifactVersionStore()
    >>> store.store(artifact)          # version becomes '1.0.0'
    >>> store.store(updated_artifact)  # version becomes '1.0.1'
    >>> store.history('product_vision')
    [ArtifactVersion(..., version='1.0.0'), ArtifactVersion(..., version='1.0.1')]
    """

    def __init__(self) -> None:
        # name → ordered list of ArtifactVersion
        self._history: dict[str, list[ArtifactVersion]] = {}

    def store(self, artifact: Artifact) -> str:
        """Add *artifact* to the version history and return the assigned version.

        If this is the first version the version string is taken from
        ``artifact.metadata.version`` (default ``'1.0.0'``).  Subsequent
        versions are obtained by bumping the patch component of the previous
        version.

        Parameters
        ----------
        artifact:
            The artifact to store.  The method does **not** mutate the
            artifact's ``metadata.version`` — it only records the version
            internally.

        Returns
        -------
        str
            The version string assigned to this entry.
        """
        history = self._history.setdefault(artifact.name, [])
        if history:
            version = _bump_version(history[-1].version)
        else:
            version = artifact.metadata.version or '1.0.0'

        entry = ArtifactVersion(
            artifact_id=artifact.artifact_id,
            name=artifact.name,
            version=version,
            content=artifact.content,
            metadata_snapshot={
                'source_agent': artifact.metadata.source_agent,
                'source_step': artifact.metadata.source_step,
                'project_id': artifact.metadata.project_id,
                'correlation_id': artifact.metadata.correlation_id,
                'labels': dict(artifact.metadata.labels),
                'created_at': artifact.metadata.created_at.isoformat(),
            },
        )
        history.append(entry)
        return version

    def history(self, name: str) -> list[ArtifactVersion]:
        """Return the full version history for artifact *name* (oldest first).

        Returns an empty list if *name* has never been stored.
        """
        return list(self._history.get(name, []))

    def latest(self, name: str) -> ArtifactVersion | None:
        """Return the most recent version of artifact *name*, or ``None``."""
        history = self._history.get(name)
        return history[-1] if history else None

    def get_version(self, name: str, version: str) -> ArtifactVersion | None:
        """Return a specific *version* of artifact *name*, or ``None``."""
        for entry in self._history.get(name, []):
            if entry.version == version:
                return entry
        return None
