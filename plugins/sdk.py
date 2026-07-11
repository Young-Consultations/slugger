"""Plugin SDK — developer toolkit for building Slugger plugins.

:class:`PluginSDK` provides the high-level factory and validation utilities
that plugin authors use to create, test, and register plugins without directly
depending on Slugger internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from plugins.base import BasePlugin
from plugins.metadata import PluginMetadata
from plugins.registry import PluginRegistry


@dataclass
class PluginManifest:
    """Declarative plugin description loaded from a plugin package.

    This is the *plugin-author-facing* counterpart to
    :class:`~plugins.metadata.PluginMetadata`.  It adds authorship and
    licensing information as well as a ``main`` entry-point class path.

    Parameters
    ----------
    name:
        Plugin identifier (e.g. ``'my-awesome-plugin'``).
    version:
        SemVer version string.
    description:
        One-line description.
    author:
        Author name or organisation.
    license:
        SPDX licence identifier (e.g. ``'MIT'``).
    main:
        Dotted Python import path for the plugin class
        (e.g. ``'my_plugin.MyPlugin'``).
    capabilities:
        List of capability names this plugin provides.
    requires:
        Slugger version requirement (semver specifier, e.g. ``'>=0.1.0'``).
    metadata:
        Arbitrary key/value annotations.
    """

    name: str
    version: str
    description: str = ''
    author: str = ''
    license: str = 'MIT'
    main: str = ''
    capabilities: list[str] = field(default_factory=list)
    requires: str = '>=0.1.0'
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_plugin_metadata(self) -> PluginMetadata:
        """Convert to the runtime :class:`~plugins.metadata.PluginMetadata`."""
        return PluginMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            entry_point=self.main,
            capabilities=self.capabilities,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'license': self.license,
            'main': self.main,
            'capabilities': self.capabilities,
            'requires': self.requires,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'PluginManifest':
        return cls(
            name=data['name'],
            version=data.get('version', '0.1.0'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            license=data.get('license', 'MIT'),
            main=data.get('main', ''),
            capabilities=data.get('capabilities', []),
            requires=data.get('requires', '>=0.1.0'),
            metadata=data.get('metadata', {}),
        )


@dataclass
class ValidationReport:
    """Result of validating a plugin manifest."""

    manifest_name: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PluginSDK:
    """High-level toolkit for plugin authors.

    Parameters
    ----------
    registry:
        The :class:`~plugins.registry.PluginRegistry` to register plugins into.
        If ``None`` a new registry is created.

    Examples
    --------
    >>> sdk = PluginSDK()
    >>> manifest = sdk.create_manifest('my-plugin', '1.0.0', 'My plugin')
    >>> report = sdk.validate(manifest)
    >>> report.valid
    True
    """

    def __init__(self, registry: PluginRegistry | None = None) -> None:
        self._registry = registry or PluginRegistry()

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def create_manifest(
        self,
        name: str,
        version: str,
        description: str,
        author: str = '',
        capabilities: list[str] | None = None,
        **kwargs: Any,
    ) -> PluginManifest:
        """Convenience factory for a :class:`PluginManifest`."""
        return PluginManifest(
            name=name,
            version=version,
            description=description,
            author=author,
            capabilities=capabilities or [],
            **kwargs,
        )

    def validate(self, manifest: PluginManifest) -> ValidationReport:
        """Validate a plugin manifest.

        Checks:

        * ``name`` must be non-empty and contain only ``[a-z0-9-]``.
        * ``version`` must be non-empty.
        * ``main`` must be non-empty when capabilities are declared.
        * No name conflicts with already-registered plugins.

        Returns
        -------
        ValidationReport
        """
        import re
        errors: list[str] = []
        warnings: list[str] = []

        if not manifest.name:
            errors.append("Plugin 'name' must not be empty.")
        elif not re.match(r'^[a-z0-9][a-z0-9\-]*$', manifest.name):
            errors.append("Plugin 'name' must match [a-z0-9][a-z0-9-]*.")

        if not manifest.version:
            errors.append("Plugin 'version' must not be empty.")

        if manifest.capabilities and not manifest.main:
            warnings.append("'main' entry point is not set — the plugin cannot be loaded at runtime.")

        if not manifest.description:
            warnings.append("'description' is empty — provide a one-line description.")

        return ValidationReport(
            manifest_name=manifest.name,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register *plugin* into the SDK's registry."""
        self._registry.register(plugin)
