"""Main Slugger orchestrator."""

from __future__ import annotations

from orchestrator.context import ApplicationContext


class Slugger:
    def __init__(self, context: ApplicationContext) -> None:
        self.context = context

    def run_workflow(self, workflow_name: str):
        return self.context.workflow_engine.run(workflow_name)

    def list_agents(self) -> list[str]:
        return self.context.agents.list()

    def list_workflows(self) -> list[str]:
        return self.context.workflow_engine.list_workflows()

    def status(self) -> dict[str, object]:
        return {
            'environment': self.context.settings.environment,
            'providers': self.context.providers.list(),
            'agents': len(self.context.agents.list()),
            'workflows': self.context.workflow_engine.list_workflows(),
            'telemetry': self.context.reporter.summarize(),
        }
