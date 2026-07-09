"""Tests for the Planning agent.

These tests verify that the Planning agent:
- Accepts architecture input from prior steps
- Generates a project plan using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.planning import PlanningAgent


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock plan response to: {prompt[:50]}..."}


def test_planning_agent_success():
    agent = PlanningAgent()
    provider = MockProvider()
    out = agent.execute({
        "architecture_text": "System has microservices architecture with APIs",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "project_plan_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "project_plan"


def test_planning_agent_from_artifact():
    """Test that agent can extract architecture from artifact dict."""
    agent = PlanningAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "architecture",
            "content": "System has microservices, APIs, databases",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact"]["type"] == "project_plan"


def test_planning_agent_no_architecture():
    agent = PlanningAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "architecture" in out["message"].lower()


def test_planning_agent_no_provider():
    agent = PlanningAgent()
    out = agent.execute({"architecture_text": "test"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()
