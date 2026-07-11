"""Tests for the Canva design agent workflow."""

from __future__ import annotations

import pytest

from agents.architecture.canva_design_agent import CanvaDesignAgent
from models.artifact import DiagramArtifact, DocumentArtifact
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
    assert len(artifacts) == 1
    assert artifacts[0].name == 'design_artifact'
    assert 'd1' in artifacts[0].content


def test_execute_without_design_id_uses_first(agent: CanvaDesignAgent) -> None:
    context = _context()
    artifacts = agent.execute(context)
    assert len(artifacts) == 1
    assert 'Architecture Diagram' in artifacts[0].content


def test_execute_export_url_in_content(agent: CanvaDesignAgent) -> None:
    context = _context(design_id='d1', export_format='pdf')
    artifacts = agent.execute(context)
    assert 'Export URL' in artifacts[0].content


def test_execute_no_designs_returns_placeholder() -> None:
    empty_svc = MockCanvaService()
    agent = CanvaDesignAgent(empty_svc)
    context = _context()
    artifacts = agent.execute(context)
    assert len(artifacts) == 1
    assert 'No Canva designs' in artifacts[0].content


def test_execute_unknown_design_id_raises() -> None:
    svc = MockCanvaService()
    agent = CanvaDesignAgent(svc)
    context = _context(design_id='nonexistent')
    with pytest.raises(Exception):
        agent.execute(context)
