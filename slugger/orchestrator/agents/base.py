from abc import ABC, abstractmethod
from typing import Any, Dict


class Agent(ABC):
    """Base class / interface for all agents.

    Agents should be lightweight, single-responsibility components that accept
    an inputs dict and return an outputs dict. Concrete agents should inherit
    from this class to preserve a common contract.
    """

    name: str = "base_agent"

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent task.

        Args:
            inputs: A dictionary containing inputs required by the agent.

        Returns:
            A dictionary with agent outputs (may include status, artifacts, etc.).
        """
        raise NotImplementedError
