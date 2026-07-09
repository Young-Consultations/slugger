"""Test the orchestrator running a full pipeline with the first three agents.

This integration test demonstrates the orchestrator coordinating Requirements,
Business Analyst, and Architecture agents in sequence, with output from each
step fed into the next.
"""
from typing import Any, Dict

from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.config import ProviderConfig


class MockProvider:
    """Mock provider for deterministic testing."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "prompt": prompt,
            "response": f"Mock output for prompt ending with: ...{prompt[-40:]}",
        }


def test_orchestrator_pipeline_requirements_to_architecture():
    """Run a full pipeline: request -> requirements -> analysis -> architecture."""
    # Create orchestrator with mock provider
    orch = Orchestrator(provider=MockProvider())

    # Register the three agents
    orch.register_agent(RequirementsAgent())
    orch.register_agent(BusinessAnalystAgent())
    orch.register_agent(ArchitectureAgent())

    # Define the pipeline as a sequence of agent names
    pipeline = ["requirements", "business_analyst", "architecture"]

    # Run the pipeline with an initial request
    result = orch.run_pipeline(
        pipeline,
        context={
            "request": "Build a real-time collaborative document editor",
        },
    )

    # Verify the pipeline produced outputs
    assert result["status"] == "success", "Orchestrator should report success"
    # Each agent should have stored its output in the context as 'artifact'
    assert "artifact" in result, "Final artifact should be present"
    assert result["artifact"]["type"] == "architecture", "Final artifact should be architecture"

    # Verify memory registered artifacts
    assert len(orch.memory.artifact_registry) == 3, "Should have registered 3 artifacts"
    assert "requirements_v1" in orch.memory.artifact_registry
    assert "business_analysis_v1" in orch.memory.artifact_registry
    assert "architecture_v1" in orch.memory.artifact_registry

    # Verify workflow progress tracking
    assert len(orch.workflow.progress) == 3, "Should have 3 execution progress records"
    for record in orch.workflow.progress:
        assert record["status"] == "success"
