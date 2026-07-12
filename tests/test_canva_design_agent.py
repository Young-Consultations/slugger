"""Tests for the Canva design agent workflow."""

from __future__ import annotations

import pytest

from agents.architecture.canva_design_agent import CanvaDesignAgent
from models.artifact import ArtifactStatus, DiagramArtifact, DocumentArtifact
from models.execution import ExecutionContext
from services.canva import CanvaDesign, CanvaExportFormat, MockCanvaService


@pytest.fixture()
def service() -> MockCanvaService:
    svc = MockCanvaService()
    svc.designs = [CanvaDesign(design_id='d1', title='Architecture Diagram')]
    return svc


@pytest.fixture()
def agent(service: MockCanvaService) -> CanvaDesignAgent:
    return CanvaDesignAgent(service)


def _context(design_id: str | None = None, export_format: str = 'pdf') -> ExecutionContext:
    metadata: dict[str, str] = {'export_format': export_format}
    if design_id:
        metadata['design_id'] = design_id
    return ExecutionContext(
        workflow_name='design-workflow',
        step_name='design',
        project_id='proj-1',
        inputs={},
        metadata=metadata,
    )


# ---------------------------------------------------------------------------
# Agent metadata
# ---------------------------------------------------------------------------


def test_agent_external_interface(agent: CanvaDesignAgent) -> None:
    assert agent.metadata.external_interface == 'canva'


def test_agent_name(agent: CanvaDesignAgent) -> None:
    assert agent.metadata.name == 'canva_design_agent'


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def test_execute_with_design_id(agent: CanvaDesignAgent) -> None:
    context = _context(design_id='d1')
    artifacts = agent.execute(context)
    # CC-006: now returns design_brief, design_manifest, and design_artifact
    assert len(artifacts) == 3
    names = [a.name for a in artifacts]
    assert 'design_brief' in names
    assert 'design_manifest' in names
    assert 'design_artifact' in names
    design_art = next(a for a in artifacts if a.name == 'design_artifact')
    assert 'd1' in design_art.content


def test_execute_without_design_id_uses_first(agent: CanvaDesignAgent) -> None:
    context = _context()
    artifacts = agent.execute(context)
    assert len(artifacts) == 3
    design_art = next(a for a in artifacts if a.name == 'design_artifact')
    assert 'Architecture Diagram' in design_art.content


def test_execute_export_url_in_content(agent: CanvaDesignAgent) -> None:
    context = _context(design_id='d1', export_format='pdf')
    artifacts = agent.execute(context)
    design_art = next(a for a in artifacts if a.name == 'design_artifact')
    assert 'Export URL' in design_art.content


def test_execute_no_designs_returns_placeholder() -> None:
    empty_svc = MockCanvaService()
    agent = CanvaDesignAgent(empty_svc)
    context = _context()
    artifacts = agent.execute(context)
    # CC-006: manual handoff — returns design_brief + handoff artifact
    assert len(artifacts) == 2
    handoff = next(a for a in artifacts if a.name == 'design_artifact')
    assert handoff.extra.get('requires_manual_handoff') is True


def test_execute_unknown_design_id_returns_manual_handoff() -> None:
    """When the design ID doesn't exist, the agent enters manual handoff state."""
    svc = MockCanvaService()
    agent = CanvaDesignAgent(svc)
    context = _context(design_id='nonexistent')
    artifacts = agent.execute(context)
    # Should produce manual handoff, not raise
    assert len(artifacts) == 2
    handoff = next(a for a in artifacts if a.name == 'design_artifact')
    assert handoff.extra.get('requires_manual_handoff') is True


def test_manual_handoff_enters_awaiting_design_state() -> None:
    agent = CanvaDesignAgent(MockCanvaService())
    artifacts = agent.execute(_context())
    handoff = next(a for a in artifacts if a.name == 'design_artifact')
    assert handoff.status == ArtifactStatus.AWAITING_DESIGN
    assert handoff.extra.get('status') == 'awaiting_design'
