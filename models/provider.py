"""Provider domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(str, Enum):
    """Supported provider categories."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CODEX = "codex"
    MOCK = "mock"
    CUSTOM = "custom"


@dataclass(slots=True)
class ProviderConfig:
    """Configuration for a provider implementation."""

    name: str
    provider_type: ProviderType
    model: str = "stub-model"
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


# ---------------------------------------------------------------------------
# Typed provider request / result models (WP-001)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GenerationRequest:
    """Request model for text or code generation."""

    prompt: str
    language: str = "Python"
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GenerationResult:
    """Result model for text or code generation."""

    content: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewRequest:
    """Request model for code or prompt review."""

    code: str
    language: str = "Python"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ReviewResult:
    """Result model for code review."""

    summary: str
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RefactorRequest:
    """Request model for code refactoring."""

    code: str
    instruction: str
    language: str = "Python"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RefactorResult:
    """Result model for code refactoring."""

    refactored_code: str
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddingRequest:
    """Request model for embeddings."""

    texts: list[str]
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddingResult:
    """Result model for embeddings."""

    embeddings: list[list[float]]
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HealthResult:
    """Result model for provider health checks."""

    provider: str
    available: bool
    model: str = ""
    latency_ms: float | None = None
    has_credentials: bool = False
    reachable: bool = False
    diagnostics: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class UsageRecord:
    """Tracks token/cost usage for a provider call."""

    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
