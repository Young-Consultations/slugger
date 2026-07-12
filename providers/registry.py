"""Provider registry."""

from __future__ import annotations

from providers.base import BaseProvider


class ProviderRegistry:
    """Registers and resolves provider instances by name."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, name: str, provider: BaseProvider) -> None:
        self._providers[name] = provider

    def resolve(self, name: str) -> BaseProvider:
        try:
            return self._providers[name]
        except KeyError as error:
            raise KeyError(f"Unknown provider: {name}") from error

    def list(self) -> list[str]:
        return sorted(self._providers)
