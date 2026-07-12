"""Plugin registry."""

from __future__ import annotations

from plugins.base import BasePlugin
from plugins.loader import PluginLoader


class PluginRegistry:
    """Registers plugins and supports discovery-driven loading."""

    def __init__(self, loader: PluginLoader | None = None) -> None:
        self.loader = loader or PluginLoader()
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        self._plugins[plugin.metadata.name] = plugin

    def resolve(self, name: str) -> BasePlugin:
        return self._plugins[name]

    def list(self) -> list[str]:
        return sorted(self._plugins)

    def load_all(self) -> None:
        loaded: set[str] = set()
        remaining = dict(self._plugins)
        while remaining:
            progress = False
            for name, plugin in list(remaining.items()):
                if all(
                    dependency in loaded for dependency in plugin.metadata.dependencies
                ):
                    plugin.load()
                    loaded.add(name)
                    remaining.pop(name)
                    progress = True
            if not progress:
                raise RuntimeError(
                    f"Unable to resolve plugin dependencies: {', '.join(sorted(remaining))}"
                )

    def unload_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.unload()
