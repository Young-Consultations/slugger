"""Base plugin class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from plugins.metadata import PluginMetadata


class BasePlugin(ABC):
    """Abstract base class for Slugger plugins."""

    def __init__(self, metadata: PluginMetadata) -> None:
        self.metadata = metadata
        self.loaded = False

    @abstractmethod
    def load(self) -> None:
        """Load plugin resources into the runtime."""

    @abstractmethod
    def unload(self) -> None:
        """Unload plugin resources from the runtime."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return plugin health information."""
