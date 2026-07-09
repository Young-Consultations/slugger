"""Test the orchestrator running the full pipeline with all four agents.

This integration test demonstrates the orchestrator coordinating Requirements,
Business Analyst, Architecture, and Planning agents in sequence, with output
from each step fed into the next.
"""
from typing import Any, Dict

from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.agents.planning import PlanningAgent


class MockProvider:
    """Mock provider for deterministic testing."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "prompt": prompt,
            "response": f"Mock output for prompt ending with: ...{prompt[-40:]}",
        }


def test_orchestrator_full_pipeline_to_planning():
    """Run full pipeline: request -> requirements -> analysis -> architecture -> plan."""
    # Create orchestrator with mock provider
    orch = Orchestrator(provider=MockProvider())

    # Register all four agents
    orch.register_agent(RequirementsAgent())
    orch.register_agent(BusinessAnalystAgent())
    orch.register_agent(ArchitectureAgent())
    orch.register_agent(PlanningAgent())

    # Define the full pipeline
    pipeline = ["requirements", "business_analyst", "architecture", "planning"]

    # Run the pipeline with an initial request
    result = orch.run_pipeline(
        pipeline,
        context={
            "request": "Build a real-time collaborative document editor with offline support",
        },
    )

    # Verify the pipeline produced outputs
    assert result["status"] == "success", "Orchestrator should report success"
    # Final artifact should be the project plan
    assert "artifact" in result, "Final artifact should be present"
    assert result["artifact"]["type"] == "project_plan", "Final artifact should be project plan"

    # Verify memory registered all artifacts
    assert len(orch.memory.artifact_registry) == 4, "Should have registered 4 artifacts"
    assert "requirements_v1" in orch.memory.artifact_registry
    assert "business_analysis_v1" in orch.memory.artifact_registry
    assert "architecture_v1" in orch.memory.artifact_registry
    assert "project_plan_v1" in orch.memory.artifact_registry

    # Verify workflow progress tracking
    assert len(orch.workflow.progress) == 4, "Should have 4 execution progress records"
    for record in orch.workflow.progress:
        assert record["status"] == "success"
