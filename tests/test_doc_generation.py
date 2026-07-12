"""Tests for TASK-064: Documentation Generation."""

from __future__ import annotations


from agents.base import BaseAgent
from agents.registry import AgentRegistry
from docs.generator import AgentDocPage, DocGenerator, WorkflowDocPage
from models import AgentCapability, AgentMetadata, DocumentArtifact
from models.execution import ExecutionContext


class _FakeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name="fake_agent",
                version="1.0.0",
                description="A fake agent for testing",
                category="planning",
                outputs=["fake_output"],
            ),
            capabilities=[AgentCapability(name="fake", description="Does nothing")],
        )

    def _execute(self, context: ExecutionContext) -> list:
        return [
            self.create_artifact(context, "fake_output", "content", DocumentArtifact)
        ]


def test_agent_doc_page_to_markdown() -> None:
    page = AgentDocPage(
        agent_name="code_gen",
        category="development",
        description="Generates code",
        inputs=["requirements"],
        outputs=["source_code"],
        capabilities=["generate"],
        version="2.0.0",
    )
    md = page.to_markdown()
    assert "# code_gen" in md
    assert "development" in md
    assert "requirements" in md
    assert "source_code" in md


def test_workflow_doc_page_to_markdown() -> None:
    page = WorkflowDocPage(
        name="python-project",
        version="1.0.0",
        description="Builds a Python project",
        steps=[
            {
                "name": "vision",
                "agent": "product_vision_agent",
                "outputs": ["product_vision"],
            }
        ],
        tags=["python"],
    )
    md = page.to_markdown()
    assert "# Workflow: python-project" in md
    assert "vision" in md
    assert "product_vision_agent" in md


def test_generate_agent_docs(tmp_path) -> None:
    registry = AgentRegistry()
    registry.register(_FakeAgent())
    gen = DocGenerator(tmp_path / "docs")
    paths = gen.generate_agent_docs(registry)
    assert len(paths) >= 1
    assert any(p.name == "fake_agent.md" for p in paths)
    content = (tmp_path / "docs" / "agents" / "fake_agent.md").read_text()
    assert "fake_agent" in content


def test_generate_workflow_docs(tmp_path) -> None:
    recipe_dir = tmp_path / "recipes"
    recipe_dir.mkdir()
    (recipe_dir / "demo.yaml").write_text(
        "name: demo\nversion: 1.0.0\ndescription: Demo workflow\nsteps:\n  - name: step1\n    agent: a\n",
        encoding="utf-8",
    )
    gen = DocGenerator(tmp_path / "docs")
    paths = gen.generate_workflow_docs(recipe_dir)
    assert len(paths) == 1
    content = paths[0].read_text()
    assert "# Workflow: demo" in content


def test_generate_index(tmp_path) -> None:
    gen = DocGenerator(tmp_path / "docs")
    gen.generate_agent_docs(AgentRegistry())  # create empty agents dir
    index = gen.generate_index()
    assert index.exists()
    assert "Reference Documentation" in index.read_text()
