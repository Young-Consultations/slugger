"""Workflow step executor."""

from __future__ import annotations

from models.execution import ExecutionContext
from validators.quality_gate import QualityGateEvaluator
from workflow.models import StepInstance


class StepExecutor:
    def __init__(self, agent_registry, quality_gate_evaluator: QualityGateEvaluator) -> None:
        self.agent_registry = agent_registry
        self.quality_gate_evaluator = quality_gate_evaluator

    def execute(self, workflow_name: str, project_id: str, step_instance: StepInstance, available_artifacts: dict[str, object], metadata: dict[str, str] | None = None):
        agent = self.agent_registry.resolve(step_instance.definition.agent)
        inputs = {name: available_artifacts[name] for name in step_instance.definition.inputs if name in available_artifacts}
        prior_artifacts = [a for a in available_artifacts.values() if hasattr(a, 'artifact_id')]
        context = ExecutionContext(
            project_id=project_id,
            workflow_name=workflow_name,
            step_name=step_instance.definition.name,
            inputs=inputs,
            artifacts=prior_artifacts,
            metadata=dict(metadata or {}),
        )
        artifacts = agent.execute(context)
        results = []
        for artifact in artifacts:
            step_instance.artifacts.append(artifact)
            results.extend(self.quality_gate_evaluator.evaluate(step_instance.definition.quality_gates, artifact))
        return artifacts, results
