"""Tests for the Testing agent.

These tests verify that the Testing agent:
- Accepts code or architecture input from prior steps
- Generates test scaffolds using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.testing import TestingAgent


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock test scaffold for: {prompt[:50]}..."}


def test_testing_agent_success():
    agent = TestingAgent()
    provider = MockProvider()
    out = agent.execute({
        "code_text": "class UserService: def create_user(self, name): pass",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "test_scaffold_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "test_scaffold"


def test_testing_agent_from_artifact():
    """Test that agent can extract code from artifact dict."""
    agent = TestingAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "code_scaffold",
            "content": "Project structure with main.py and services",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact"]["type"] == "test_scaffold"


def test_testing_agent_from_architecture():
    """Test that agent can extract architecture if no code is provided."""
    agent = TestingAgent()
    provider = MockProvider()
    out = agent.execute({
        "architecture_text": "Microservices with REST APIs and databases",
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_testing_agent_no_context():
    agent = TestingAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "code" in out["message"].lower() or "architecture" in out["message"].lower()


def test_testing_agent_no_provider():
    agent = TestingAgent()
    out = agent.execute({"code_text": "test code"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()
