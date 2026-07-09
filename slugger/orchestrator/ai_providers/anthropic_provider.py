from typing import Any, Dict, Optional

from .base import AIProvider


class AnthropicProvider(AIProvider):
    """A minimal stub for an Anthropic Claude provider adapter.

    Like the OpenAI stub, this class does not perform network requests. It
    provides a predictable response shape and accepts an api_key parameter for
    later extension to a real SDK-backed implementation.
    """

    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        response_text = f"[stubbed {self.name} response] {prompt}"
        return {"provider": self.name, "prompt": prompt, "response": response_text}
