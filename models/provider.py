"""Provider domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProviderType(str, Enum):
    """Supported provider categories."""

    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    MOCK = 'mock'
    CUSTOM = 'custom'


@dataclass(slots=True)
class ProviderConfig:
    """Configuration for a provider implementation."""

    name: str
    provider_type: ProviderType
    model: str = 'stub-model'
    api_key: str | None = None
    api_key_env: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 30
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Provider:
    """Registered provider instance metadata."""

    name: str
    provider_type: ProviderType
    config: ProviderConfig
    available: bool = True
