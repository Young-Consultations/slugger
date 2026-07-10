"""OpenAI provider stub."""

from __future__ import annotations

import os

from models.provider import ProviderConfig
from providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """Stub implementation for an OpenAI-backed provider."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._api_key = os.getenv(config.api_key_env or 'OPENAI_API_KEY')

    def complete(self, prompt: str, **kwargs: object) -> str:
        return f'OpenAI stub response for model {self.config.model}: TODO implement API call. Prompt preview: {prompt[:80]}'

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_metadata(self) -> dict[str, str]:
        return {'provider': 'openai', 'model': self.config.model, 'status': 'stub'}
