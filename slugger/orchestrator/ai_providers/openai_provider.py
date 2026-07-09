from typing import Any, Dict, Optional

from .base import AIProvider


class OpenAIProvider(AIProvider):
    """A minimal stub for an OpenAI provider adapter.

    This implementation is intentionally lightweight and does not call any
    external network services. It provides a controlled, testable response for
    development and unit tests.
    """

    name = "openai"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        # NOTE: Replace this stub with a real SDK integration in a follow-up task.
        response_text = f"[stubbed {self.name} response] {prompt}"
        return {"provider": self.name, "prompt": prompt, "response": response_text}
