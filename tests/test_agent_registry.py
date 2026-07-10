from agents.planning.product_vision_agent import ProductVisionAgent
from agents.registry import AgentRegistry


def test_agent_registry_resolves_by_name_and_capability() -> None:
    registry = AgentRegistry()
    agent = ProductVisionAgent()
    registry.register(agent)
    assert registry.resolve(agent.metadata.name) is agent
    assert registry.by_capability('product_vision') == [agent]
