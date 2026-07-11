"""Main Slugger orchestrator."""

from __future__ import annotations

from models.project import ProjectInput
from orchestrator.context import ApplicationContext
from workflow.models import WorkflowInstance

_DEFAULT_WORKFLOW = 'full-sdlc'


class Slugger:
    def __init__(self, context: ApplicationContext) -> None:
        self.context = context

    def run_workflow(self, workflow_name: str):
        return self.context.workflow_engine.run(workflow_name)

    def build(self, project_input: ProjectInput, workflow: str | None = None) -> WorkflowInstance:
        """Run a workflow initialised with the supplied :class:`ProjectInput`.

        Parameters
        ----------
        project_input:
            A :class:`~models.project.ProjectInput` describing the app idea,
            target platform, and preferred coding agent.
        workflow:
            Optional workflow name or YAML path.  Defaults to ``full-sdlc``.
        """

        workflow_name = workflow or _DEFAULT_WORKFLOW
        metadata = project_input.as_metadata()
        return self.context.workflow_engine.run(workflow_name, metadata=metadata)

    def resume(self, run_id: str, project_input: ProjectInput | None = None) -> WorkflowInstance:
        """Resume a previously interrupted workflow run.

        Parameters
        ----------
        run_id:
            The run identifier returned by a prior :meth:`build` call
            (``result.run_id``).
        project_input:
            Optional project input whose metadata is forwarded to remaining
            steps.  If omitted the steps receive no metadata.
        """

        metadata = project_input.as_metadata() if project_input is not None else None
        return self.context.workflow_engine.resume(run_id, metadata=metadata)

    def list_agents(self) -> list[str]:
        return self.context.agents.list()

    def list_workflows(self) -> list[str]:
        return self.context.workflow_engine.list_workflows()

    def status(self) -> dict[str, object]:
        provider_names = self.context.providers.list()
        provider_health: dict[str, object] = {}
        for name in provider_names:
            try:
                provider = self.context.providers.resolve(name)
                health = provider.health_check()
                provider_health[name] = {
                    'available': health.available,
                    'model': health.model,
                    'has_credentials': health.has_credentials,
                }
            except Exception as exc:  # noqa: BLE001
                provider_health[name] = {'available': False, 'error': str(exc)}
        lineage_node_count = len(self.context.lineage_graph.all_nodes())
        knowledge_doc_count = 0
        if self.context.knowledge_indexer is not None:
            knowledge_doc_count = len(self.context.knowledge_indexer.documents)
        return {
            'environment': self.context.settings.environment,
            'providers': provider_names,
            'provider_health': provider_health,
            'agents': len(self.context.agents.list()),
            'workflows': self.context.workflow_engine.list_workflows(),
            'services': {
                'github': type(self.context.github).__name__,
                'chatgpt': type(self.context.chatgpt).__name__ if self.context.chatgpt else 'none',
                'canva': type(self.context.canva).__name__ if self.context.canva else 'none',
            },
            'lineage': {
                'nodes': lineage_node_count,
            },
            'knowledge': {
                'documents': knowledge_doc_count,
            },
            'observability': {
                'cost_usd': self.context.cost_tracker.total_cost(),
                'failures': len(self.context.failure_analytics.failures()),
            },
            'telemetry': self.context.reporter.summarize(),
        }

    def lineage(self) -> dict[str, object]:
        """Return the current artifact lineage graph as a serialisable dict."""
        return self.context.lineage_graph.to_dict()
