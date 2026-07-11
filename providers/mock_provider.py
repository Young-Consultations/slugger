"""Mock provider implementation for tests and offline execution."""

from __future__ import annotations

from collections import deque

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

    # ------------------------------------------------------------------
    # Typed capability methods
    # ------------------------------------------------------------------

    def generate(self, request: GenerationRequest) -> GenerationResult:
        content = self.complete(request.prompt)
        return GenerationResult(content=content, model=self.config.model, input_tokens=10, output_tokens=10)

    def review(self, request: ReviewRequest) -> ReviewResult:
        return ReviewResult(
            summary='Mock review: code looks acceptable.',
            issues=[],
            suggestions=['Consider adding docstrings.'],
            score=8.0,
        )

    def refactor(self, request: RefactorRequest) -> RefactorResult:
        return RefactorResult(refactored_code=request.code, model=self.config.model)

    def embed_typed(self, request: EmbeddingRequest) -> EmbeddingResult:
        return EmbeddingResult(
            embeddings=self.embed(request.texts),
            model=self.config.model,
        )

    def health_check(self) -> HealthResult:
        return HealthResult(
            provider=self.config.name,
            available=True,
            model=self.config.model,
            has_credentials=True,
            reachable=True,
            diagnostics={'status': 'ready', 'mode': 'mock'},
        )
