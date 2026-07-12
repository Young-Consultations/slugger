"""Application context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agents.messaging import MessageBus
from agents.registry import AgentRegistry
from config.settings import Settings
from knowledge.indexer import KnowledgeIndexer
from memory.memory_manager import MemoryManager
from models.artifact_lineage import LineageGraph
from models.artifact_store import InMemoryArtifactStore
from observability.collector import MetricsCollector
from observability.cost_tracker import CostTracker
from observability.dashboard import FailureAnalytics, MetricsDashboard
from observability.reporter import ObservabilityReporter
from observability.telemetry import TelemetryCollector
from observability.token_budget import TokenBudget
from observability.tracer import ExecutionTracer
from providers.capabilities import CapabilityResolver
from providers.codex_agent_client import ICodexAgentClient
from providers.registry import ProviderRegistry
from services.canva.base import ICanvaService
from services.chatgpt.base import IChatGPTService
from services.github.base import IGitHubService
from workflow.engine import WorkflowEngine

if TYPE_CHECKING:
    from prompts.catalog import SdlcPromptCatalog


@dataclass(slots=True)
class ApplicationContext:
    settings: Settings
    providers: ProviderRegistry
    agents: AgentRegistry
    workflow_engine: WorkflowEngine
    artifact_store: InMemoryArtifactStore
    memory: MemoryManager
    github: IGitHubService
    metrics: MetricsCollector
    tracer: ExecutionTracer
    reporter: ObservabilityReporter
    message_bus: MessageBus = field(default_factory=MessageBus)
    lineage_graph: LineageGraph = field(default_factory=LineageGraph)
    cost_tracker: CostTracker = field(default_factory=CostTracker)
    token_budget: TokenBudget = field(default_factory=TokenBudget)
    telemetry: TelemetryCollector = field(default_factory=TelemetryCollector)
    failure_analytics: FailureAnalytics = field(default_factory=FailureAnalytics)
    knowledge_indexer: KnowledgeIndexer | None = None
    chatgpt: IChatGPTService | None = None
    canva: ICanvaService | None = None
    codex_agent_client: ICodexAgentClient | None = None
    prompt_catalog: SdlcPromptCatalog | None = None
    capability_resolver: CapabilityResolver | None = None
    """Runtime capability resolver; populated by :class:`Bootstrap` (CC-003)."""

    def dashboard(self) -> MetricsDashboard:
        """Return a :class:`~observability.dashboard.MetricsDashboard` view."""
        return MetricsDashboard(self.metrics, self.tracer, self.failure_analytics)
