"""Tests for Epic 3: artifact lineage model."""

from __future__ import annotations


from agents.architecture.system_design_agent import SystemDesignAgent
from agents.planning.product_vision_agent import ProductVisionAgent
from agents.planning.requirements_agent import RequirementsAgent
from agents.planning.user_story_agent import UserStoryAgent
from agents.registry import AgentRegistry
from models.artifact_lineage import ArtifactLineageNode, LineageGraph, SdlcStage
from validators import ArtifactValidator, QualityGateEvaluator
from workflow.executor import StepExecutor
from workflow.models import StepInstance, WorkflowStepDefinition


# ---------------------------------------------------------------------------
# Node creation
# ---------------------------------------------------------------------------


def test_node_to_dict() -> None:
    node = ArtifactLineageNode(
        artifact_id="code-1",
        name="generated_code",
        stage=SdlcStage.CODE,
        parent_ids=["req-1"],
        agent_name="code_generator_agent",
    )
    data = node.to_dict()
    assert data["artifact_id"] == "code-1"
    assert data["stage"] == "code"
    assert "req-1" in data["parent_ids"]


# ---------------------------------------------------------------------------
# LineageGraph
# ---------------------------------------------------------------------------


def _build_sdlc_graph() -> LineageGraph:
    """Build a minimal SDLC lineage graph for testing."""
    graph = LineageGraph()
    nodes = [
        ArtifactLineageNode("idea-1", "product_idea", SdlcStage.IDEA),
        ArtifactLineageNode(
            "req-1", "requirements", SdlcStage.REQUIREMENTS, parent_ids=["idea-1"]
        ),
        ArtifactLineageNode(
            "story-1", "user_stories", SdlcStage.STORIES, parent_ids=["req-1"]
        ),
        ArtifactLineageNode(
            "arch-1", "architecture", SdlcStage.ARCHITECTURE, parent_ids=["req-1"]
        ),
        ArtifactLineageNode("adr-1", "adr", SdlcStage.ADR, parent_ids=["arch-1"]),
        ArtifactLineageNode(
            "task-1", "tasks", SdlcStage.TASKS, parent_ids=["story-1", "arch-1"]
        ),
        ArtifactLineageNode(
            "code-1", "source_code", SdlcStage.CODE, parent_ids=["task-1"]
        ),
        ArtifactLineageNode("test-1", "tests", SdlcStage.TESTS, parent_ids=["code-1"]),
        ArtifactLineageNode(
            "release-1", "release", SdlcStage.RELEASE, parent_ids=["test-1"]
        ),
    ]
    for node in nodes:
        graph.add(node)
    return graph


def test_add_and_get() -> None:
    graph = LineageGraph()
    node = ArtifactLineageNode("a1", "artifact", SdlcStage.CODE)
    graph.add(node)
    assert graph.get("a1") is node


def test_get_missing_returns_none() -> None:
    graph = LineageGraph()
    assert graph.get("nonexistent") is None


def test_ancestors_direct_parent() -> None:
    graph = _build_sdlc_graph()
    ancestors = graph.ancestors("req-1")
    assert any(n.artifact_id == "idea-1" for n in ancestors)


def test_ancestors_transitive() -> None:
    graph = _build_sdlc_graph()
    ancestors = graph.ancestors("release-1")
    ancestor_ids = {n.artifact_id for n in ancestors}
    assert "idea-1" in ancestor_ids
    assert "req-1" in ancestor_ids
    assert "code-1" in ancestor_ids


def test_ancestors_root_has_no_ancestors() -> None:
    graph = _build_sdlc_graph()
    assert graph.ancestors("idea-1") == []


def test_descendants_direct_child() -> None:
    graph = _build_sdlc_graph()
    descendants = graph.descendants("req-1")
    desc_ids = {n.artifact_id for n in descendants}
    assert "story-1" in desc_ids
    assert "arch-1" in desc_ids


def test_descendants_leaf_has_no_descendants() -> None:
    graph = _build_sdlc_graph()
    assert graph.descendants("release-1") == []


def test_chain_ends_with_target() -> None:
    graph = _build_sdlc_graph()
    chain = graph.chain("release-1")
    assert chain[-1].artifact_id == "release-1"


def test_chain_starts_with_root() -> None:
    graph = _build_sdlc_graph()
    chain = graph.chain("release-1")
    assert chain[0].stage == SdlcStage.IDEA


def test_nodes_by_stage() -> None:
    graph = _build_sdlc_graph()
    code_nodes = graph.nodes_by_stage(SdlcStage.CODE)
    assert len(code_nodes) == 1
    assert code_nodes[0].artifact_id == "code-1"


def test_all_nodes_count() -> None:
    graph = _build_sdlc_graph()
    assert len(graph.all_nodes()) == 9


def test_remove() -> None:
    graph = _build_sdlc_graph()
    graph.remove("idea-1")
    assert graph.get("idea-1") is None


def test_to_dict_structure() -> None:
    graph = _build_sdlc_graph()
    data = graph.to_dict()
    assert "nodes" in data
    assert len(data["nodes"]) == 9


def test_lineage_traces_idea_to_system_design_chain() -> None:
    registry = AgentRegistry()
    for agent in (
        ProductVisionAgent(),
        RequirementsAgent(),
        UserStoryAgent(),
        SystemDesignAgent(),
    ):
        registry.register(agent)
    graph = LineageGraph()
    executor = StepExecutor(
        registry,
        QualityGateEvaluator({"artifact_validator": ArtifactValidator()}),
        lineage_graph=graph,
    )
    available_artifacts = {}
    metadata = {"idea": "Build a planner app"}
    steps = [
        WorkflowStepDefinition(name="product_vision", agent="product_vision_agent"),
        WorkflowStepDefinition(
            name="requirements", agent="requirements_agent", inputs=["product_vision"]
        ),
        WorkflowStepDefinition(
            name="user_stories",
            agent="user_story_agent",
            inputs=["product_vision", "requirements"],
        ),
        WorkflowStepDefinition(
            name="system_design",
            agent="system_design_agent",
            inputs=["requirements", "user_stories"],
        ),
    ]
    for step_definition in steps:
        step_instance = StepInstance(definition=step_definition)
        artifacts, _ = executor.execute(
            "wf", "proj-1", step_instance, available_artifacts, metadata=metadata
        )
        for artifact in artifacts:
            available_artifacts[artifact.name] = artifact
    design_artifact = available_artifacts["system_design"]
    chain = graph.chain(design_artifact.artifact_id)
    assert [node.name for node in chain] == [
        "idea",
        "product_vision",
        "requirements",
        "user_stories",
        "system_design",
    ]
