"""OpenAI Codex provider for code generation tasks.

Extends :class:`~providers.openai_provider.OpenAIProvider` with a dedicated
code-completions endpoint and code-generation helpers.
"""

from __future__ import annotations

import os

import requests

from core.exceptions import ProviderError
from models.provider import (
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

_OPENAI_API_BASE = "https://api.openai.com/v1"

# Default Codex/code-focused model (the chat-completions family now covers
# code generation; gpt-4o is used as the default here but can be overridden
# via config.model to any code-focused model such as 'gpt-4o', 'gpt-4-turbo',
# or a fine-tuned variant).
_DEFAULT_CODEX_MODEL = "gpt-4o"


class CodexProvider(BaseProvider):
    """OpenAI Codex-backed provider specialised for code generation.

    Builds a structured system prompt that instructs the model to return only
    well-formatted source code and uses the chat-completions endpoint.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._api_key = config.api_key or os.getenv(
            config.api_key_env or "OPENAI_API_KEY"
        )
        self._base_url = (config.base_url or _OPENAI_API_BASE).rstrip("/")
        self._model = config.model or _DEFAULT_CODEX_MODEL

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ProviderError(
                "OpenAI API key is not configured. "
                "Set OPENAI_API_KEY or supply api_key in secrets."
            )
        return {
            "Authorization": "Bearer " + self._api_key,
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # BaseProvider interface
    # ------------------------------------------------------------------

    def complete(self, prompt: str, **kwargs: object) -> str:
        """Generate a code completion for *prompt*.

        Parameters
        ----------
        prompt:
            Natural-language description of the code to generate, or a
            partial code block to complete.
        **kwargs:
            Optional overrides forwarded to the API:
            ``temperature``, ``max_tokens``, ``top_p``, ``stop``,
            ``language`` (used to build the system message only).
        """
        headers = self._auth_headers()
        language = str(kwargs.pop("language", "Python"))
        system_msg = (
            f"You are an expert {language} engineer. "
            "Respond with only clean, well-structured, production-ready source code. "
            "Do not include any prose, markdown fences, or explanations unless "
            "they appear as code comments inside the returned source."
        )
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        }
        for key in ("temperature", "max_tokens", "top_p", "n", "stop"):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"Codex API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Codex request failed: {exc}") from exc
        data = response.json()
        choices = data.get("choices", [])
        if not choices or "message" not in choices[0]:
            raise ProviderError(f"Unexpected Codex response structure: {data}")
        return choices[0]["message"]["content"]

    def _review_raw(
        self, code: str, *, language: str = "Python", **kwargs: object
    ) -> str:
        """Request a code review for *code*.

        Returns structured review feedback as a string.
        """
        system_msg = (
            f"You are a senior {language} code reviewer. "
            "Analyse the provided code and return a structured review with sections: "
            "Summary, Issues (numbered list), Suggestions (numbered list), "
            "and an overall quality score out of 10."
        )
        headers = self._auth_headers()
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": f"Review the following {language} code:\n\n{code}",
                },
            ],
        }
        for key in ("temperature", "max_tokens"):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"Codex review API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Codex review request failed: {exc}") from exc
        choices = response.json().get("choices", [])
        if not choices or "message" not in choices[0]:
            raise ProviderError("Unexpected Codex review response structure.")
        return choices[0]["message"]["content"]

    def _refactor_raw(
        self, code: str, instruction: str, *, language: str = "Python", **kwargs: object
    ) -> str:
        """Refactor *code* according to *instruction*.

        Returns the refactored source code as a string.
        """
        system_msg = (
            f"You are an expert {language} engineer specialised in refactoring. "
            "Apply the given instruction to the provided code and return only the "
            "refactored source code with no additional commentary."
        )
        prompt = f"Instruction: {instruction}\n\nCode:\n\n{code}"
        headers = self._auth_headers()
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
        }
        for key in ("temperature", "max_tokens"):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"Codex refactor API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Codex refactor request failed: {exc}") from exc
        choices = response.json().get("choices", [])
        if not choices or "message" not in choices[0]:
            raise ProviderError("Unexpected Codex refactor response structure.")
        return choices[0]["message"]["content"]

    def embed(self, texts: list[str]) -> list[list[float]]:
        headers = self._auth_headers()
        embed_model = self.config.metadata.get(
            "embedding_model", "text-embedding-3-small"
        )
        payload: dict[str, object] = {"model": embed_model, "input": texts}
        try:
            response = requests.post(
                f"{self._base_url}/embeddings",
                json=payload,
                headers=headers,
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"Codex embeddings API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"Codex embeddings request failed: {exc}") from exc
        data = response.json()["data"]
        return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_metadata(self) -> dict[str, str]:
        return {
            "provider": "codex",
            "model": self._model,
            "status": "ready" if self.is_available() else "no_key",
        }

    # ------------------------------------------------------------------
    # Typed capability methods (WP-001)
    # ------------------------------------------------------------------

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate code from a typed :class:`~models.provider.GenerationRequest`."""
        kwargs: dict[str, object] = {"language": request.language}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        content = self.complete(request.prompt, **kwargs)
        return GenerationResult(
            content=content,
            model=self._model,
            # Note: token counts are rough whitespace-word approximations; for accurate
            # billing-grade counts use a tokenizer library such as tiktoken.
            input_tokens=len(request.prompt.split()),
            output_tokens=len(content.split()),
        )

    def review(self, request: ReviewRequest) -> ReviewResult:
        """Review code using a typed :class:`~models.provider.ReviewRequest`."""
        raw = self._review_raw(request.code, language=request.language)
        return ReviewResult(summary=raw, score=7.0)

    def refactor(self, request: RefactorRequest) -> RefactorResult:
        """Refactor code using a typed :class:`~models.provider.RefactorRequest`."""
        raw = self._refactor_raw(
            request.code, request.instruction, language=request.language
        )
        return RefactorResult(refactored_code=raw, model=self._model)

    def health_check(self) -> HealthResult:
        """Return a health check for the Codex provider."""
        available = self.is_available()
        return HealthResult(
            provider="codex",
            available=available,
            model=self._model,
            has_credentials=available,
            reachable=False,
            diagnostics={"status": "ready" if available else "no_key"},
        )
