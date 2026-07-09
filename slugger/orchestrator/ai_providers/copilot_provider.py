from typing import Any, Dict, Optional

from .base import AIProvider


class CopilotProvider(AIProvider):
    """A minimal stub for a GitHub Copilot provider adapter.

    Copilot does not currently offer a public REST SDK in the same style as
    others; this adapter is a placeholder for future integration with any
    available Copilot APIs or internal connectors.
    """

    name = "copilot"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        response_text = f"[stubbed {self.name} response] {prompt}"
        return {"provider": self.name, "prompt": prompt, "response": response_text}
