"""Tests for the Deployment agent.

These tests verify that the Deployment agent:
- Accepts code, documentation, or deployment context from prior steps
- Generates deployment configurations using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.deployment import DeploymentAgent


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock deployment config for: {prompt[:50]}..."}


def test_deployment_agent_success():
    agent = DeploymentAgent()
    provider = MockProvider()
    out = agent.execute({
        "code_text": "class API: def main(): pass",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "deployment_config_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "deployment_config"


def test_deployment_agent_from_artifact():
    """Test that agent can extract code from artifact dict."""
    agent = DeploymentAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "documentation",
            "content": "Deployment and scaling instructions",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact"]["type"] == "deployment_config"


def test_deployment_agent_from_documentation():
    """Test that agent can extract documentation."""
    agent = DeploymentAgent()
    provider = MockProvider()
    out = agent.execute({
        "documentation_text": "API runs on port 8080, uses PostgreSQL",
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_deployment_agent_no_context():
    agent = DeploymentAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "code" in out["message"].lower() or "documentation" in out["message"].lower()


def test_deployment_agent_no_provider():
    agent = DeploymentAgent()
    out = agent.execute({"code_text": "test code"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()
