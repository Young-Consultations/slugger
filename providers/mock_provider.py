"""Mock provider implementation for tests and offline execution."""

from __future__ import annotations

from collections import deque

from models.provider import ProviderConfig
from providers.base import BaseProvider


class MockProvider(BaseProvider):
    """Provider returning deterministic configurable responses."""

    def __init__(self, config: ProviderConfig, responses: list[str] | None = None) -> None:
        super().__init__(config)
        self._responses: deque[str] = deque(responses or ['mock response'])

    def complete(self, prompt: str, **kwargs: object) -> str:
        if len(self._responses) > 1:
            return self._responses.popleft()
        return self._responses[0]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), float(len(text))] for index, text in enumerate(texts)]

    def is_available(self) -> bool:
        return True

    def get_metadata(self) -> dict[str, str]:
        return {'provider': 'mock', 'model': self.config.model, 'status': 'ready'}
