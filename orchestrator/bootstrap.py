"""Application bootstrap."""

from __future__ import annotations

from pathlib import Path

from agents import ADRAgent, APIDesignAgent, AgentRegistry, CICDAgent, ChangelogAgent, CodeGeneratorAgent, CodeReviewAgent, DeploymentAgent, DiagramAgent, DocumentationAgent, GitHubIssuesAgent, KnowledgeAgent, MonitoringAgent, PerformanceAgent, ProductVisionAgent, ProjectPlanAgent, RefactorAgent, ReflectionAgent, ReleaseAgent, RequirementsAgent, SecurityReviewAgent, SystemDesignAgent, TestGeneratorAgent, TestRunnerAgent, UserStoryAgent
from config.loader import ConfigLoader
from memory import FileMemoryBackend, InMemoryBackend, MemoryManager
from models.artifact_store import InMemoryArtifactStore
from models.provider import ProviderConfig, ProviderType
from observability import ExecutionTracer, MetricsCollector, ObservabilityReporter
from orchestrator.context import ApplicationContext
from providers import AnthropicProvider, MockProvider, OpenAIProvider, ProviderRegistry
from services.github import IGitHubService, MockGitHubService
from validators import AgentValidator, ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser


class Bootstrap:
    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def build(self, config_path: str | None = None) -> ApplicationContext:
        settings = ConfigLoader(self.root_path).load(config_path)
        providers = ProviderRegistry()
        for name, config in settings.providers.configs.items():
            if config.provider_type == ProviderType.OPENAI:
                providers.register(name, OpenAIProvider(config))
            elif config.provider_type == ProviderType.ANTHROPIC:
                providers.register(name, AnthropicProvider(config))
            else:
                providers.register(name, MockProvider(config))
        if 'mock' not in providers.list():
            providers.register('mock', MockProvider(ProviderConfig(name='mock', provider_type=ProviderType.MOCK)))
        artifact_store = InMemoryArtifactStore()
        backend = InMemoryBackend() if settings.memory.backend == 'in_memory' else FileMemoryBackend(self.root_path / settings.memory.storage_path)
        memory = MemoryManager(backend)
        metrics = MetricsCollector()
        tracer = ExecutionTracer()
        reporter = ObservabilityReporter(metrics, tracer)
        validators = {'artifact_validator': ArtifactValidator(), 'workflow_validator': WorkflowValidator(), 'agent_validator': AgentValidator()}
        agents = self._build_agents()
        parser = WorkflowParser(validators['workflow_validator'])
        executor = StepExecutor(agents, QualityGateEvaluator({'artifact_validator': validators['artifact_validator']}))
        workflow_engine = WorkflowEngine(self.root_path / settings.workflow.recipe_directory, parser, executor, artifact_store)
        github_settings = settings.github
        if github_settings.token and github_settings.owner and github_settings.repo:
            from services.github import GitHubClient
            github_service: IGitHubService = GitHubClient(
                owner=github_settings.owner,
                repo=github_settings.repo,
                token=github_settings.token,
            )
        else:
            github_service = MockGitHubService()
        return ApplicationContext(settings=settings, providers=providers, agents=agents, workflow_engine=workflow_engine, artifact_store=artifact_store, memory=memory, github=github_service, metrics=metrics, tracer=tracer, reporter=reporter)

    def _build_agents(self) -> AgentRegistry:
        registry = AgentRegistry()
        planning_agents = [ProductVisionAgent(), RequirementsAgent(), UserStoryAgent(), ProjectPlanAgent()]
        architecture_agents = [SystemDesignAgent(), ADRAgent(), DiagramAgent(), APIDesignAgent()]
        development_agents = [CodeGeneratorAgent(), CodeReviewAgent(), RefactorAgent(), DocumentationAgent()]
        qa_agents = [TestGeneratorAgent(), TestRunnerAgent(), SecurityReviewAgent(), PerformanceAgent()]
        operations_agents = [DeploymentAgent(), CICDAgent(), MonitoringAgent(), ReleaseAgent()]
        support_agents = [KnowledgeAgent(), GitHubIssuesAgent(), ChangelogAgent(), ReflectionAgent()]
        for agent in planning_agents + architecture_agents + development_agents + qa_agents + operations_agents + support_agents:
            registry.register(agent)
        return registry
