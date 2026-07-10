"""Plugin metadata models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PluginMetadata:
    """Describes a loadable plugin."""

    name: str
    version: str
    description: str
    entry_point: str | None = None
    capabilities: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
