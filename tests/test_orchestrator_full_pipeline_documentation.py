"""Test the orchestrator running the full pipeline with all seven agents.

This integration test demonstrates the orchestrator coordinating Requirements,
Business Analyst, Architecture, Planning, Coding, Testing, and Documentation
agents in sequence.
"""
from typing import Any, Dict

from slugger.orchestrator.core import Orchestrator
from slugger.orchestrator.agents.requirements import RequirementsAgent
from slugger.orchestrator.agents.business_analyst import BusinessAnalystAgent
from slugger.orchestrator.agents.architecture import ArchitectureAgent
from slugger.orchestrator.agents.planning import PlanningAgent
from slugger.orchestrator.agents.coding import CodingAgent
from slugger.orchestrator.agents.testing import TestingAgent
from slugger.orchestrator.agents.documentation import DocumentationAgent


class MockProvider:
    """Mock provider for deterministic testing."""
    name = "mock"

    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        return {
            "provider": "mock",
            "prompt": prompt,
            "response": f"Mock output for prompt ending with: ...{prompt[-40:]}",
        }


def test_orchestrator_full_pipeline_to_documentation():
    """Run full pipeline: request -> ... -> testing -> documentation."""
    # Create orchestrator with mock provider
    orch = Orchestrator(provider=MockProvider())

    # Register all seven agents
    orch.register_agent(RequirementsAgent())
    orch.register_agent(BusinessAnalystAgent())
    orch.register_agent(ArchitectureAgent())
    orch.register_agent(PlanningAgent())
    orch.register_agent(CodingAgent())
    orch.register_agent(TestingAgent())
    orch.register_agent(DocumentationAgent())

    # Define the full pipeline
    pipeline = ["requirements", "business_analyst", "architecture", "planning", "coding", "testing", "documentation"]

    # Run the pipeline with an initial request
    result = orch.run_pipeline(
        pipeline,
        context={
            "request": "Build a real-time collaborative document editor with offline support",
        },
    )

    # Verify the pipeline produced outputs
    assert result["status"] == "success", "Orchestrator should report success"
    # Final artifact should be the documentation
    assert "artifact" in result, "Final artifact should be present"
    assert result["artifact"]["type"] == "documentation", "Final artifact should be documentation"

    # Verify memory registered all artifacts
    assert len(orch.memory.artifact_registry) == 7, "Should have registered 7 artifacts"
    assert "requirements_v1" in orch.memory.artifact_registry
    assert "business_analysis_v1" in orch.memory.artifact_registry
    assert "architecture_v1" in orch.memory.artifact_registry
    assert "project_plan_v1" in orch.memory.artifact_registry
    assert "code_scaffold_v1" in orch.memory.artifact_registry
    assert "test_scaffold_v1" in orch.memory.artifact_registry
    assert "documentation_v1" in orch.memory.artifact_registry

    # Verify workflow progress tracking
    assert len(orch.workflow.progress) == 7, "Should have 7 execution progress records"
    for record in orch.workflow.progress:
        assert record["status"] == "success"
