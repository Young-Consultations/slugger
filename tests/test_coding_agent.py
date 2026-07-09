"""Tests for the Coding agent.

These tests verify that the Coding agent:
- Accepts plan or architecture input from prior steps
- Generates code scaffolds using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.coding import CodingAgent


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock code scaffold for: {prompt[:50]}..."}


def test_coding_agent_success():
    agent = CodingAgent()
    provider = MockProvider()
    out = agent.execute({
        "plan_text": "Phase 1: Setup project structure and dependencies. Phase 2: Implement APIs.",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "code_scaffold_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "code_scaffold"


def test_coding_agent_from_artifact():
    """Test that agent can extract plan from artifact dict."""
    agent = CodingAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "project_plan",
            "content": "Project phases and milestones defined",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact"]["type"] == "code_scaffold"


def test_coding_agent_from_architecture():
    """Test that agent can extract architecture if no plan is provided."""
    agent = CodingAgent()
    provider = MockProvider()
    out = agent.execute({
        "architecture_text": "Microservices with REST APIs",
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_coding_agent_no_context():
    agent = CodingAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "plan" in out["message"].lower() or "architecture" in out["message"].lower()


def test_coding_agent_no_provider():
    agent = CodingAgent()
    out = agent.execute({"plan_text": "test plan"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()
