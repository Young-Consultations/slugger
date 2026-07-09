"""Tests for the Documentation agent.

These tests verify that the Documentation agent:
- Accepts code, architecture, or requirements input from prior steps
- Generates documentation using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.documentation import DocumentationAgent


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock documentation for: {prompt[:50]}..."}


def test_documentation_agent_success():
    agent = DocumentationAgent()
    provider = MockProvider()
    out = agent.execute({
        "code_text": "class API: def get_users(self): pass",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "documentation_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "documentation"


def test_documentation_agent_from_artifact():
    """Test that agent can extract code from artifact dict."""
    agent = DocumentationAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "code_scaffold",
            "content": "Project structure with API endpoints",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact"]["type"] == "documentation"


def test_documentation_agent_from_architecture():
    """Test that agent can extract architecture if no code is provided."""
    agent = DocumentationAgent()
    provider = MockProvider()
    out = agent.execute({
        "architecture_text": "Microservices with REST APIs",
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_documentation_agent_from_requirements():
    """Test that agent can extract requirements."""
    agent = DocumentationAgent()
    provider = MockProvider()
    out = agent.execute({
        "requirements_text": "Must support real-time collaboration",
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_documentation_agent_no_context():
    agent = DocumentationAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "code" in out["message"].lower() or "architecture" in out["message"].lower()


def test_documentation_agent_no_provider():
    agent = DocumentationAgent()
    out = agent.execute({"code_text": "test code"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()
