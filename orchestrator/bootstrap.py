"""Application bootstrap."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from agents import ADRAgent, APIDesignAgent, AgentRegistry, CICDAgent, ChangelogAgent, CodeGeneratorAgent, CodeReviewAgent, DeploymentAgent, DiagramAgent, DocumentationAgent, GitHubIssuesAgent, KnowledgeAgent, MonitoringAgent, PerformanceAgent, ProductVisionAgent, ProjectPlanAgent, RefactorAgent, ReflectionAgent, ReleaseAgent, RequirementsAgent, SecurityReviewAgent, SystemDesignAgent, TestGeneratorAgent, TestRunnerAgent, UserStoryAgent
from agents.architecture.canva_design_agent import CanvaDesignAgent
from agents.messaging import MessageBus
from config.loader import ConfigLoader
from knowledge.indexer import KnowledgeIndexer
from memory import FileMemoryBackend, InMemoryBackend, MemoryManager
from models.artifact_store import InMemoryArtifactStore
from models.provider import ProviderConfig, ProviderType
from observability import ExecutionTracer, MetricsCollector, ObservabilityReporter
from observability.cost_tracker import CostTracker
from observability.dashboard import FailureAnalytics
from observability.telemetry import TelemetryCollector
from observability.token_budget import TokenBudget
from orchestrator.context import ApplicationContext
from providers import AnthropicProvider, CodexProvider, MockProvider, OpenAIProvider, ProviderRegistry
from services.canva import ICanvaService, MockCanvaService
from services.chatgpt import IChatGPTService, MockChatGPTService
from services.github import IGitHubService, MockGitHubService
from validators import AgentValidator, ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser, WorkflowPersistence


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
            elif config.provider_type == ProviderType.CODEX:
                providers.register(name, CodexProvider(config))
            else:
                providers.register(name, MockProvider(config))
        if 'mock' not in providers.list():
            providers.register('mock', MockProvider(ProviderConfig(name='mock', provider_type=ProviderType.MOCK)))
        # Register Codex provider when OPENAI_API_KEY is present and codex is not yet registered.
        # Codex is registered separately from the openai provider so it gets the correct
        # ProviderType.CODEX discriminator for capability routing.
        if 'codex' not in providers.list():
            codex_key = os.environ.get('OPENAI_API_KEY', '')
            if codex_key:
                chatgpt_settings = getattr(settings, 'chatgpt', None)
                codex_model = getattr(chatgpt_settings, 'model', 'gpt-4o') if chatgpt_settings is not None else 'gpt-4o'
                providers.register('codex', CodexProvider(ProviderConfig(name='codex', provider_type=ProviderType.CODEX, api_key=codex_key, model=codex_model)))
        artifact_store = InMemoryArtifactStore()
        backend = InMemoryBackend() if settings.memory.backend == 'in_memory' else FileMemoryBackend(self.root_path / settings.memory.storage_path)
        memory = MemoryManager(backend)
        message_bus = MessageBus()
        from models.artifact_lineage import LineageGraph
        lineage_graph = LineageGraph()
        metrics = MetricsCollector()
        tracer = ExecutionTracer()
        reporter = ObservabilityReporter(metrics, tracer)
        cost_tracker = CostTracker()
        token_budget = TokenBudget()
        telemetry = TelemetryCollector()
        failure_analytics = FailureAnalytics()
        knowledge_indexer = self._build_knowledge_indexer()
        validators = {'artifact_validator': ArtifactValidator(), 'workflow_validator': WorkflowValidator(), 'agent_validator': AgentValidator()}
        canva_service = self._build_canva_service(settings)
        chatgpt_service = self._build_chatgpt_service(settings)
        agents = self._build_agents(canva_service)
        parser = WorkflowParser(validators['workflow_validator'])
        executor = StepExecutor(agents, QualityGateEvaluator({'artifact_validator': validators['artifact_validator']}), message_bus=message_bus, lineage_graph=lineage_graph, chatgpt_service=chatgpt_service)
        persistence = WorkflowPersistence(self.root_path / settings.workflow.state_store)
        workflow_engine = WorkflowEngine(self.root_path / settings.workflow.recipe_directory, parser, executor, artifact_store, persistence=persistence)
        github_settings = settings.github
        if github_settings.token and github_settings.owner and github_settings.repo:
            from services.github import GitHubClient
            github_service: IGitHubService = GitHubClient(
                owner=github_settings.owner,
                repo=github_settings.repo,
                token=github_settings.token,
            )
        else:
            token = os.environ.get(github_settings.token_env, '')
            if token and github_settings.owner and github_settings.repo:
                from services.github import GitHubClient
                github_service = GitHubClient(owner=github_settings.owner, repo=github_settings.repo, token=token)
            else:
                github_service = MockGitHubService()
        strict_mode = getattr(getattr(settings, 'environment', None), 'strict_mode', False) if hasattr(settings, 'environment') else False
        if isinstance(strict_mode, str):
            strict_mode = strict_mode.lower() in ('true', '1', 'yes')
        from providers.capabilities import CapabilityResolver
        capability_resolver = CapabilityResolver(
            provider_registry=providers,
            strict_mode=bool(strict_mode),
        )
        return ApplicationContext(
            settings=settings,
            providers=providers,
            agents=agents,
            workflow_engine=workflow_engine,
            artifact_store=artifact_store,
            memory=memory,
            github=github_service,
            metrics=metrics,
            tracer=tracer,
            reporter=reporter,
            message_bus=message_bus,
            lineage_graph=lineage_graph,
            cost_tracker=cost_tracker,
            token_budget=token_budget,
            telemetry=telemetry,
            failure_analytics=failure_analytics,
            knowledge_indexer=knowledge_indexer,
            chatgpt=chatgpt_service,
            canva=canva_service,
            capability_resolver=capability_resolver,
        )

    def _build_canva_service(self, settings: object) -> ICanvaService:
        """Resolve the Canva service — live client if credentials present, mock otherwise."""
        canva_settings = getattr(settings, 'canva', None)
        if canva_settings is None:
            return MockCanvaService()
        token = canva_settings.access_token or os.environ.get(canva_settings.access_token_env, '')
        if token:
            from services.canva import CanvaClient
            return CanvaClient(access_token=token, base_url=canva_settings.base_url)
        return MockCanvaService()

    def _build_chatgpt_service(self, settings: object) -> IChatGPTService:
        """Resolve the ChatGPT service — live client if credentials present, mock otherwise."""
        chatgpt_settings = getattr(settings, 'chatgpt', None)
        if chatgpt_settings is None:
            return MockChatGPTService()
        if getattr(chatgpt_settings, 'mock_mode', False):
            return MockChatGPTService()
        api_key = chatgpt_settings.api_key or os.environ.get(chatgpt_settings.api_key_env, '')
        if api_key:
            from services.chatgpt import ChatGPTClient
            return ChatGPTClient(
                api_key=api_key,
                model=chatgpt_settings.model,
                base_url=chatgpt_settings.base_url,
                timeout=chatgpt_settings.timeout_seconds,
            )
        return MockChatGPTService()

    def _build_agents(self, canva_service: ICanvaService | None = None) -> AgentRegistry:
        registry = AgentRegistry()
        planning_agents = [ProductVisionAgent(), RequirementsAgent(), UserStoryAgent(), ProjectPlanAgent()]
        architecture_agents = [SystemDesignAgent(), ADRAgent(), DiagramAgent(), APIDesignAgent()]
        if canva_service is not None:
            architecture_agents.append(CanvaDesignAgent(canva_service))
        development_agents = [CodeGeneratorAgent(), CodeReviewAgent(), RefactorAgent(), DocumentationAgent()]
        qa_agents = [TestGeneratorAgent(), TestRunnerAgent(), SecurityReviewAgent(), PerformanceAgent()]
        operations_agents = [DeploymentAgent(), CICDAgent(), MonitoringAgent(), ReleaseAgent()]
        support_agents = [KnowledgeAgent(), GitHubIssuesAgent(), ChangelogAgent(), ReflectionAgent()]
        for agent in planning_agents + architecture_agents + development_agents + qa_agents + operations_agents + support_agents:
            registry.register(agent)
        return registry

    def _build_knowledge_indexer(self) -> KnowledgeIndexer | None:
        """Build and index the knowledge base if the directory exists."""
        knowledge_dir = self.root_path / 'knowledge'
        if knowledge_dir.is_dir():
            indexer = KnowledgeIndexer(knowledge_dir)
            try:
                indexer.index()
            except Exception as exc:  # noqa: BLE001
                logging.getLogger(__name__).warning(
                    'Knowledge indexing failed for %s: %s', knowledge_dir, exc
                )
            return indexer
        return None
