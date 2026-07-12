"""Workflow step executor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.messaging import MessageBus
from models.artifact_lineage import ArtifactLineageNode, LineageGraph, SdlcStage
from models.execution import ExecutionContext
from models.project import ProjectBrief
from validators.quality_gate import QualityGateEvaluator
from workflow.models import StepInstance

if TYPE_CHECKING:
    from prompts.catalog import SdlcPromptCatalog

# Maps step name keywords to SDLC stages for automatic lineage tagging
_STAGE_KEYWORDS: list[tuple[str, SdlcStage]] = [
    ('vision', SdlcStage.IDEA),
    ('requirements', SdlcStage.REQUIREMENTS),
    ('story', SdlcStage.STORIES),
    ('stories', SdlcStage.STORIES),
    ('architecture', SdlcStage.ARCHITECTURE),
    ('design', SdlcStage.ARCHITECTURE),
    ('adr', SdlcStage.ADR),
    ('plan', SdlcStage.TASKS),
    ('task', SdlcStage.TASKS),
    ('code', SdlcStage.CODE),
    ('generate', SdlcStage.CODE),
    ('develop', SdlcStage.CODE),
    ('test', SdlcStage.TESTS),
    ('review', SdlcStage.TESTS),
    ('secur', SdlcStage.TESTS),
    ('release', SdlcStage.RELEASE),
    ('deploy', SdlcStage.RELEASE),
    ('doc', SdlcStage.RELEASE),
]


def _infer_stage(step_name: str) -> SdlcStage:
    """Infer the SDLC stage from a step name."""
    lower = step_name.lower()
    for keyword, stage in _STAGE_KEYWORDS:
        if keyword in lower:
            return stage
    return SdlcStage.CODE


def _idea_root_node(project_id: str, idea: str) -> ArtifactLineageNode:
    return ArtifactLineageNode(
        artifact_id=f'idea::{project_id}',
        name='idea',
        stage=SdlcStage.IDEA,
        agent_name='workflow',
        project_id=project_id,
        metadata={'idea': idea},
    )


class StepExecutor:
    def __init__(
        self,
        agent_registry,
        quality_gate_evaluator: QualityGateEvaluator,
        message_bus: MessageBus | None = None,
        lineage_graph: LineageGraph | None = None,
        chatgpt_service: object | None = None,
        prompt_catalog: SdlcPromptCatalog | None = None,
    ) -> None:
        self.agent_registry = agent_registry
        self.quality_gate_evaluator = quality_gate_evaluator
        self.message_bus = message_bus
        self.lineage_graph = lineage_graph
        self.chatgpt_service = chatgpt_service
        self.prompt_catalog = prompt_catalog

    def execute(
        self,
        workflow_name: str,
        project_id: str,
        step_instance: StepInstance,
        available_artifacts: dict[str, object],
        metadata: dict[str, str] | None = None,
        project_brief: ProjectBrief | None = None,
    ):
        agent = self.agent_registry.resolve(step_instance.definition.agent)
        inputs = {name: available_artifacts[name] for name in step_instance.definition.inputs if name in available_artifacts}
        prior_artifacts = [a for a in available_artifacts.values() if hasattr(a, 'artifact_id')]
        parent_ids = [aid for a in prior_artifacts if (aid := getattr(a, 'artifact_id', None)) is not None]
        idea_root_id = None
        idea = ''
        if metadata:
            idea = str(metadata.get('idea', ''))
        if self.lineage_graph is not None and idea:
            root = _idea_root_node(project_id, idea)
            idea_root_id = root.artifact_id
            if self.lineage_graph.get(idea_root_id) is None:
                self.lineage_graph.add(root)
        if not parent_ids and idea_root_id is not None:
            parent_ids = [idea_root_id]
        # Resolve project brief from the explicit argument or from metadata (supports resume).
        resolved_brief = project_brief
        if resolved_brief is None and metadata:
            resolved_brief = ProjectBrief.from_metadata(dict(metadata))
        context = ExecutionContext(
            project_id=project_id,
            workflow_name=workflow_name,
            step_name=step_instance.definition.name,
            inputs=inputs,
            artifacts=prior_artifacts,
            metadata=dict(metadata or {}),
            message_bus=self.message_bus,
            project_brief=resolved_brief,
            chatgpt_service=self.chatgpt_service,
            prompt_catalog=self.prompt_catalog,
        )
        artifacts = agent.execute(context)
        results = []
        stage = _infer_stage(step_instance.definition.name)
        for artifact in artifacts:
            step_instance.artifacts.append(artifact)
            results.extend(self.quality_gate_evaluator.evaluate(step_instance.definition.quality_gates, artifact))
            # Capture lineage for this artifact
            if self.lineage_graph is not None:
                artifact_id = getattr(artifact, 'artifact_id', None)
                artifact_name = getattr(artifact, 'name', step_instance.definition.name)
                if artifact_id:
                    node = ArtifactLineageNode(
                        artifact_id=artifact_id,
                        name=artifact_name,
                        stage=stage,
                        parent_ids=parent_ids,
                        agent_name=agent.metadata.name,
                        project_id=project_id,
                    )
                    self.lineage_graph.add(node)
            # Publish artifact-ready event to the message bus if available
            if self.message_bus is not None:
                from agents.messaging import AgentMessage
                self.message_bus.publish(AgentMessage(
                    sender=agent.metadata.name,
                    recipient='*',
                    subject='artifact.ready',
                    payload={
                        'artifact_id': getattr(artifact, 'artifact_id', None),
                        'name': getattr(artifact, 'name', None),
                        'step': step_instance.definition.name,
                        'workflow': workflow_name,
                        'project_id': project_id,
                    },
                    correlation_id=project_id,
                ))
        return artifacts, results
