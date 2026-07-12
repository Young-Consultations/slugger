"""Anthropic provider implementation."""

from __future__ import annotations

import os

import requests

from core.exceptions import ProviderError
from models.provider import ProviderConfig
from providers.base import BaseProvider

_ANTHROPIC_API_BASE = "https://api.anthropic.com/v1"
_ANTHROPIC_VERSION = "2024-10-22"


class AnthropicProvider(BaseProvider):
    """Anthropic Claude-backed provider using the Messages REST API."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._api_key = config.api_key or os.getenv(
            config.api_key_env or "ANTHROPIC_API_KEY"
        )
        self._base_url = (config.base_url or _ANTHROPIC_API_BASE).rstrip("/")

    def _auth_headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ProviderError(
                "Anthropic API key is not configured. Set ANTHROPIC_API_KEY or supply api_key in secrets."
            )
        return {
            "x-api-key": self._api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

    def complete(self, prompt: str, **kwargs: object) -> str:
        headers = self._auth_headers()
        max_tokens = int(kwargs.get("max_tokens", 1024))  # type: ignore[arg-type]
        payload: dict[str, object] = {
            "model": self.config.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        for key in ("temperature", "top_p", "stop_sequences"):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f"{self._base_url}/messages",
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"Anthropic API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Anthropic request failed: {exc}") from exc
        content_blocks = response.json().get("content", [])
        text_blocks = [
            block.get("text", "")
            for block in content_blocks
            if block.get("type") == "text"
        ]
        return "\n".join(text_blocks)

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise ProviderError(
            "Anthropic does not provide a native text embedding API. Use a different provider for embeddings."
        )

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_metadata(self) -> dict[str, str]:
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "status": "ready" if self.is_available() else "no_key",
        }
