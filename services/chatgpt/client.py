"""ChatGPT REST API client."""

from __future__ import annotations

import json
import os
from typing import Any

import requests

from core.exceptions import ProviderError
from services.chatgpt.base import IChatGPTService
from services.chatgpt.models import (
    ChatGPTRole,
    ChatMessage,
    PromptExecutionResult,
    PromptReviewResult,
)

_OPENAI_API_BASE = "https://api.openai.com/v1"
_DEFAULT_MODEL = "gpt-4o"


class ChatGPTClient(IChatGPTService):
    """ChatGPT service backed by the OpenAI chat-completions REST API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._model = model
        self._base = (base_url or _OPENAI_API_BASE).rstrip("/")
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ProviderError(
                "OpenAI API key not configured. Set OPENAI_API_KEY or pass api_key."
            )
        return {
            "Authorization": "Bearer " + self._api_key,
            "Content-Type": "application/json",
        }

    def _post_chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: object,
    ) -> dict[str, Any]:
        payload: dict[str, object] = {"model": self._model, "messages": messages}
        for key in ("temperature", "max_tokens", "top_p", "stop"):
            if key in kwargs:
                payload[key] = kwargs[key]
        try:
            response = requests.post(
                f"{self._base}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise ProviderError(
                f"ChatGPT API error {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except requests.RequestException as exc:
            raise ProviderError(f"ChatGPT request failed: {exc}") from exc
        return response.json()  # type: ignore[return-value]

    def execute(
        self, prompt: str, *, system: str | None = None, **kwargs: object
    ) -> PromptExecutionResult:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": ChatGPTRole.SYSTEM.value, "content": system})
        messages.append({"role": ChatGPTRole.USER.value, "content": prompt})
        data = self._post_chat(messages, **kwargs)
        choice = (data.get("choices") or [{}])[0]
        usage = data.get("usage") or {}
        return PromptExecutionResult(
            prompt=prompt,
            response=choice.get("message", {}).get("content", ""),
            model=str(data.get("model", self._model)),
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            finish_reason=str(choice.get("finish_reason", "stop")),
        )

    def execute_conversation(
        self, messages: list[ChatMessage], **kwargs: object
    ) -> PromptExecutionResult:
        raw = [{"role": msg.role.value, "content": msg.content} for msg in messages]
        data = self._post_chat(raw, **kwargs)
        choice = (data.get("choices") or [{}])[0]
        usage = data.get("usage") or {}
        last_user = next(
            (msg.content for msg in reversed(messages) if msg.role == ChatGPTRole.USER),
            "",
        )
        return PromptExecutionResult(
            prompt=last_user,
            response=choice.get("message", {}).get("content", ""),
            model=str(data.get("model", self._model)),
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            finish_reason=str(choice.get("finish_reason", "stop")),
        )

    def review_prompt(self, prompt: str) -> PromptReviewResult:
        system = (
            "You are a prompt engineering expert. "
            "Review the following prompt for clarity, specificity, and effectiveness. "
            "Return JSON with keys: score (0-10 float), feedback (string), "
            "suggestions (list of strings), passed (bool, true if score >= 6)."
        )
        result = self.execute(prompt, system=system)
        # Parse JSON response (best-effort)
        try:
            data = json.loads(result.response)
            return PromptReviewResult(
                prompt=prompt,
                score=float(data.get("score", 0.0)),
                feedback=str(data.get("feedback", "")),
                suggestions=list(data.get("suggestions", [])),
                passed=bool(data.get("passed", False)),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return PromptReviewResult(
                prompt=prompt,
                score=0.0,
                feedback=result.response,
                suggestions=[],
                passed=False,
            )
