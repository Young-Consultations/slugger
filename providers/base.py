"""Base provider abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.exceptions import ProviderError
from models.provider import (
    EmbeddingRequest,
    EmbeddingResult,
    GenerationRequest,
    GenerationResult,
    HealthResult,
    ProviderConfig,
    RefactorRequest,
    RefactorResult,
    ReviewRequest,
    ReviewResult,
)


class UnsupportedCapabilityError(ProviderError):
    """Raised when a provider does not support the requested capability."""


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

    # ------------------------------------------------------------------
    # Typed capability methods (WP-001) — default to unsupported
    # ------------------------------------------------------------------

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text/code from a typed request.

        Subclasses should override this method to provide a typed interface.
        The default delegates to :meth:`complete`.
        """
        content = self.complete(request.prompt, language=request.language)
        meta = self.get_metadata()
        return GenerationResult(content=content, model=meta.get('model', ''))

    def review(self, request: ReviewRequest) -> ReviewResult:
        """Return a structured review.  Override for typed review support."""
        raise UnsupportedCapabilityError(
            f"Provider '{self.config.name}' does not support code review."
        )

    def refactor(self, request: RefactorRequest) -> RefactorResult:
        """Return refactored code.  Override for typed refactor support."""
        raise UnsupportedCapabilityError(
            f"Provider '{self.config.name}' does not support code refactoring."
        )

    def embed_typed(self, request: EmbeddingRequest) -> EmbeddingResult:
        """Return typed embeddings.  Override for typed embedding support."""
        embeddings = self.embed(request.texts)
        meta = self.get_metadata()
        return EmbeddingResult(embeddings=embeddings, model=meta.get('model', ''))

    def health_check(self) -> HealthResult:
        """Perform a side-effect-free health check.

        Returns a :class:`~models.provider.HealthResult` with availability,
        credential presence, and sanitized diagnostics.
        """
        meta = self.get_metadata()
        available = self.is_available()
        return HealthResult(
            provider=self.config.name,
            available=available,
            model=meta.get('model', ''),
            has_credentials=available,
            reachable=False,  # subclasses may override for live checks
            diagnostics={k: v for k, v in meta.items() if k not in ('api_key',)},
        )

    def supports_capability(self, capability: str) -> bool:
        """Return whether this provider supports the named capability.

        Built-in capabilities: ``'complete'``, ``'embed'``, ``'generate'``,
        ``'review'``, ``'refactor'``, ``'embed_typed'``.
        """
        always_supported = {'complete', 'embed', 'generate', 'embed_typed'}
        if capability in always_supported:
            return True
        # Probe optional capabilities by checking a callable method exists on this instance
        return callable(getattr(self, capability, None))
