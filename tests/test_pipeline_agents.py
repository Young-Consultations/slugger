"""Tests for the first pipeline agents (Requirements, Business Analyst, Architecture).

These tests verify that each agent:
- Accepts inputs with a provider
- Generates output using the provider
- Returns properly structured artifact metadata
- Handles missing inputs gracefully
"""
from typing import Any, Dict

from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.ai_providers.factory import ProviderFactory
from slugger.config import ProviderConfig


class MockProvider:
    """Mock provider for testing agent output shape."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {"provider": "mock", "prompt": prompt, "response": f"Mock response to: {prompt[:50]}..."}


def test_requirements_agent_success():
    agent = RequirementsAgent()
    provider = MockProvider()
    out = agent.execute({
        "request": "Build a REST API for a todo application",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "requirements_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "requirements"


def test_requirements_agent_no_request():
    agent = RequirementsAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"
    assert "request" in out["message"].lower()


def test_requirements_agent_no_provider():
    agent = RequirementsAgent()
    out = agent.execute({"request": "test"})
    assert out["status"] == "error"
    assert "provider" in out["message"].lower()


def test_business_analyst_agent_success():
    agent = BusinessAnalystAgent()
    provider = MockProvider()
    out = agent.execute({
        "requirements_text": "Functional Req: API must support CRUD operations",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "business_analysis_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "business_analysis"


def test_business_analyst_agent_from_artifact():
    """Test that agent can extract requirements from artifact dict."""
    agent = BusinessAnalystAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "requirements",
            "content": "Functional Req: API must support CRUD",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"


def test_business_analyst_agent_no_requirements():
    agent = BusinessAnalystAgent()
    out = agent.execute({"_provider": MockProvider()})
    assert out["status"] == "error"


def test_architecture_agent_success():
    agent = ArchitectureAgent()
    provider = MockProvider()
    out = agent.execute({
        "requirements_text": "Build a scalable REST API",
        "_provider": provider,
    })
    assert out["status"] == "success"
    assert out["artifact_name"] == "architecture_v1"
    assert "artifact" in out
    assert out["artifact"]["type"] == "architecture"


def test_architecture_agent_from_artifact():
    """Test that agent can extract context from artifact dict."""
    agent = ArchitectureAgent()
    provider = MockProvider()
    out = agent.execute({
        "artifact": {
            "type": "business_analysis",
            "content": "User Story: As a user, I want to create todos",
        },
        "_provider": provider,
    })
    assert out["status"] == "success"
