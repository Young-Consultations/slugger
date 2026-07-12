from dataclasses import asdict

from agents.architecture.diagram_agent import DiagramAgent
from agents.development.code_generator_agent import CodeGeneratorAgent
from agents.operations.ci_cd_agent import CICDAgent
from models import (
    DocumentArtifact,
    InMemoryArtifactStore,
    Project,
    ProjectPhase,
    ProjectStatus,
)


def test_project_defaults() -> None:
    project = Project(project_id="p1", name="Slugger", description="AI factory")
    assert project.status is ProjectStatus.DRAFT
    assert project.phase is ProjectPhase.IDEA


def test_artifact_store_round_trip() -> None:
    artifact = DocumentArtifact(artifact_id="a1", name="requirements", content="hello")
    store = InMemoryArtifactStore()
    store.create(artifact)
    assert store.get("a1") == artifact
    assert store.find_by_name("requirements") == [artifact]


def test_agent_external_interface_assignments() -> None:
    assert CodeGeneratorAgent().metadata.external_interface == "openai_codex"
    assert DiagramAgent().metadata.external_interface == "canva"
    assert CICDAgent().metadata.external_interface == "github_actions"


def test_agent_metadata_preserves_provider_with_external_interface() -> None:
    metadata = asdict(CodeGeneratorAgent().metadata)
    assert metadata["provider"] == "mock"
    assert metadata["external_interface"] == "openai_codex"
