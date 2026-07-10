"""OpenAI provider implementation."""

from __future__ import annotations

import os

import requests

from core.exceptions import ProviderError
from models.provider import ProviderConfig
from providers.base import BaseProvider

_OPENAI_API_BASE = 'https://api.openai.com/v1'


class OpenAIProvider(BaseProvider):
    """OpenAI-backed provider using the chat completions and embeddings REST APIs."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._api_key = config.api_key or os.getenv(config.api_key_env or 'OPENAI_API_KEY')
        self._base_url = (config.base_url or _OPENAI_API_BASE).rstrip('/')

    def _auth_headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ProviderError('OpenAI API key is not configured. Set OPENAI_API_KEY or supply api_key in secrets.')
        return {'Authorization': 'Bearer ' + self._api_key, 'Content-Type': 'application/json'}

    def complete(self, prompt: str, **kwargs: object) -> str:
        headers = self._auth_headers()
        payload: dict[str, object] = {
            'model': self.config.model,
            'messages': [{'role': 'user', 'content': prompt}],
        }
        for key in ('temperature', 'max_tokens', 'top_p', 'n', 'stop'):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f'{self._base_url}/chat/completions',
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(f'OpenAI API error {exc.response.status_code}: {exc.response.text}') from exc
        except requests.RequestException as exc:
            raise ProviderError(f'OpenAI request failed: {exc}') from exc
        data = response.json()
        choices = data.get('choices', [])
        if not choices or 'message' not in choices[0]:
            raise ProviderError(f'Unexpected OpenAI response structure: {data}')
        return choices[0]['message']['content']

    def embed(self, texts: list[str]) -> list[list[float]]:
        headers = self._auth_headers()
        embed_model = self.config.metadata.get('embedding_model', 'text-embedding-3-small')
        payload: dict[str, object] = {'model': embed_model, 'input': texts}
        try:
            response = requests.post(
                f'{self._base_url}/embeddings',
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(f'OpenAI embeddings API error {exc.response.status_code}: {exc.response.text}') from exc
        except requests.RequestException as exc:
            raise ProviderError(f'OpenAI embeddings request failed: {exc}') from exc
        data = response.json()['data']
        return [item['embedding'] for item in sorted(data, key=lambda x: x['index'])]

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_metadata(self) -> dict[str, str]:
        return {'provider': 'openai', 'model': self.config.model, 'status': 'ready' if self.is_available() else 'no_key'}
