"""Base provider abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.provider import ProviderConfig


class BaseProvider(ABC):
    """Abstract interface for AI and platform providers."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abstractmethod
    def complete(self, prompt: str, **kwargs: object) -> str:
        """Generate a completion for the supplied prompt."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for the supplied text batch."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the provider can currently serve requests."""

    @abstractmethod
    def get_metadata(self) -> dict[str, str]:
        """Return provider metadata for diagnostics."""
