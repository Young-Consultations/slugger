"""Generic component registry."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


class ComponentRegistry:
    """Stores components keyed by interface and optional name."""

    def __init__(self) -> None:
        self._components: dict[type[Any], dict[str, Any]] = defaultdict(dict)

    def register(self, interface: type[Any], component: Any, name: str | None = None) -> None:
        self._components[interface][name or component.__class__.__name__] = component

    def resolve(self, interface: type[Any], name: str | None = None) -> Any:
        options = self._components.get(interface, {})
        if name is None:
            return next(iter(options.values()))
        return options[name]

    def resolve_all(self, interface: type[Any]) -> list[Any]:
        return list(self._components.get(interface, {}).values())
