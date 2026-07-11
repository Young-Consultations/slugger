"""Project Manifest — captures project identity, dependencies, and build configuration.

A manifest can be persisted to / loaded from YAML so it can travel alongside
the generated project artefacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ManifestDependency:
    """A declared dependency of the project."""

    name: str
    version: str = '*'
    extras: list[str] = field(default_factory=list)


@dataclass
class ManifestBuildConfig:
    """Build / generation configuration embedded in the manifest."""

    coding_agent: str = 'codex'
    platform: str = 'web'
    workflow: str = 'python-project'
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectManifest:
    """Root manifest model for a Slugger-generated project.

    Parameters
    ----------
    project_id:
        Unique project identifier (UUID or slug).
    name:
        Human-readable project name.
    version:
        SemVer project version string.
    description:
        Short description of the project.
    dependencies:
        Runtime dependencies declared for the project.
    dev_dependencies:
        Development / tooling dependencies.
    build:
        Build and code-generation configuration.
    tags:
        Free-form labels for filtering.
    metadata:
        Arbitrary key/value pairs for custom annotations.
    """

    project_id: str
    name: str
    version: str = '0.1.0'
    description: str = ''
    dependencies: list[ManifestDependency] = field(default_factory=list)
    dev_dependencies: list[ManifestDependency] = field(default_factory=list)
    build: ManifestBuildConfig = field(default_factory=ManifestBuildConfig)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert the manifest to a JSON/YAML-serialisable dict."""

        def _dep(d: ManifestDependency) -> dict[str, Any]:
            result: dict[str, Any] = {'name': d.name, 'version': d.version}
            if d.extras:
                result['extras'] = d.extras
            return result

        return {
            'project_id': self.project_id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': [_dep(d) for d in self.dependencies],
            'dev_dependencies': [_dep(d) for d in self.dev_dependencies],
            'build': {
                'coding_agent': self.build.coding_agent,
                'platform': self.build.platform,
                'workflow': self.build.workflow,
                **self.build.extra,
            },
            'tags': self.tags,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ProjectManifest':
        """Reconstruct a :class:`ProjectManifest` from a plain dict."""

        def _dep(raw: dict[str, Any]) -> ManifestDependency:
            return ManifestDependency(
                name=raw['name'],
                version=raw.get('version', '*'),
                extras=raw.get('extras', []),
            )

        raw_build = data.get('build', {})
        known_build_keys = {'coding_agent', 'platform', 'workflow'}
        build = ManifestBuildConfig(
            coding_agent=raw_build.get('coding_agent', 'codex'),
            platform=raw_build.get('platform', 'web'),
            workflow=raw_build.get('workflow', 'python-project'),
            extra={k: v for k, v in raw_build.items() if k not in known_build_keys},
        )

        return cls(
            project_id=data['project_id'],
            name=data['name'],
            version=data.get('version', '0.1.0'),
            description=data.get('description', ''),
            dependencies=[_dep(d) for d in data.get('dependencies', [])],
            dev_dependencies=[_dep(d) for d in data.get('dev_dependencies', [])],
            build=build,
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
        )

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        """Write the manifest to *path* as YAML."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(self.to_dict(), sort_keys=False), encoding='utf-8')

    @classmethod
    def load(cls, path: Path) -> 'ProjectManifest':
        """Load a manifest from a YAML *path*."""
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        return cls.from_dict(data)
