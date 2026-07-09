from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):
    """Abstract AI provider interface.

    Implementations should wrap concrete provider SDKs and normalise responses
    into a small, predictable dictionary that the orchestrator can consume.
    """

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate a response for the given prompt.

        Args:
            prompt: The prompt text.
            **kwargs: Provider-specific options.

        Returns:
            A dict with at least a 'text' or 'response' field.
        """
        raise NotImplementedError
