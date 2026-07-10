"""Application context."""

from __future__ import annotations

from dataclasses import dataclass

from agents.registry import AgentRegistry
from config.settings import Settings
from memory.memory_manager import MemoryManager
from models.artifact_store import InMemoryArtifactStore
from observability.collector import MetricsCollector
from observability.reporter import ObservabilityReporter
from observability.tracer import ExecutionTracer
from providers.registry import ProviderRegistry
from services.github.base import IGitHubService
from workflow.engine import WorkflowEngine


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
