from typing import Any, Dict, Iterable, List, Optional

from slugger.config import ProviderConfig
from slugger.orchestrator.agent_manager import AgentManager
from slugger.orchestrator.ai_providers.factory import ProviderFactory
from slugger.orchestrator.memory import Memory
from slugger.orchestrator.workflow import WorkflowEngine
from slugger.orchestrator.agents.base import Agent
from slugger.orchestrator.ai_providers.base import AIProvider


class Orchestrator:
    """Core orchestrator that composes components and provides provider
    injection.

    This class is intentionally small and focused: it wires together the
    AgentManager, Memory and WorkflowEngine and resolves an AI provider using
    ProviderFactory. Agents are registered explicitly via register_agent.
    """

    def __init__(self, provider: Optional[AIProvider] = None, cfg: Optional[ProviderConfig] = None) -> None:
        self.agent_manager = AgentManager()
        self.memory = Memory()
        self.workflow = WorkflowEngine()
        self._cfg = cfg or ProviderConfig.from_env()
        self._provider = provider or ProviderFactory.create(cfg=self._cfg)

    @property
    def provider(self) -> AIProvider:
        return self._provider

    def register_agent(self, agent: Agent) -> None:
        self.agent_manager.register(agent)

    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agent_manager.get(name)

    def run_agent(self, name: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a registered agent by name, injecting the configured provider
        into the inputs under the key '_provider'.
        """
        agent = self.get_agent(name)
        if agent is None:
            raise ValueError(f"Agent '{name}' not found")
        ctx = dict(inputs or {})
        # provide read-only access to the provider instance via inputs
        ctx.setdefault("_provider", self.provider)
        result = agent.execute(ctx)
        # register artifact reference if agent returns artifact metadata
        if isinstance(result, dict) and "artifact" in result:
            name = result.get("artifact_name", "unnamed")
            self.memory.register_artifact(name, result.get("artifact"))
        return result

    def run_pipeline(self, steps: Iterable[Any], context: Optional[Dict[str, Any]] = None, retry: int = 0) -> Dict[str, Any]:
        """Run a sequence of steps.

        Steps may be:
        - callables that accept a context dict and return a dict
        - agent names (str) registered in the agent manager; these will be
          executed via run_agent with the current context merged into inputs

        The workflow engine performs sequential execution and retry logic.
        """
        context = context or {}

        def make_step(step):
            if isinstance(step, str):
                def run(ctx: Dict[str, Any]) -> Dict[str, Any]:
                    # pass the current context as inputs (agent may read anything)
                    inputs = dict(ctx)
                    return self.run_agent(step, inputs)

                run.__name__ = f"agent:{step}"
                return run
            elif callable(step):
                return step
            else:
                raise TypeError("Step must be a callable or a registered agent name (str)")

        callables: List[Any] = [make_step(s) for s in steps]
        return self.workflow.run_sequential(callables, context=context, retry=retry)
