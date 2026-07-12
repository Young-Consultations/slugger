"""Agent registry."""

from __future__ import annotations

from core.interfaces import IAgent


class AgentRegistry:
    """Registers and resolves agents by name or capability."""

    def __init__(self) -> None:
        self._agents: dict[str, IAgent] = {}

    def register(self, agent: IAgent) -> None:
        self._agents[agent.metadata.name] = agent

    def resolve(self, name: str) -> IAgent:
        return self._agents[name]

    def list(self) -> list[str]:
        return sorted(self._agents)

    def by_capability(self, capability: str) -> list[IAgent]:
        return [
            agent
            for agent in self._agents.values()
            if any(cap.name == capability for cap in agent.capabilities)
        ]

    def discover_from_plugins(self, plugins: list[object]) -> None:
        for plugin in plugins:
            for agent in getattr(plugin, "agents", []):
                self.register(agent)
