from typing import Dict, Optional

from .agents.base import Agent


class AgentManager:
    """Simple registry for agents.

    This manager intentionally keeps things explicit: agents must be
    instantiated and registered. This avoids dynamic import surprises during
    early development and keeps tests deterministic.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def list_agents(self) -> Dict[str, Agent]:
        return dict(self._agents)
