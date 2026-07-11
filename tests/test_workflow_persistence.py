"""Tests for persistent workflow state and resumable execution (Task 038)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agents.base import BaseAgent
from agents.registry import AgentRegistry
from models import AgentCapability, AgentMetadata, DocumentArtifact
from models.execution import ExecutionContext
from models.workflow import StepStatus
from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser, WorkflowPersistence
from workflow.models import WorkflowInstance


# ---------------------------------------------------------------------------
# Stub agents
# ---------------------------------------------------------------------------

class _VisionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(metadata=AgentMetadata(name='product_vision_agent', version='1.0.0', description='stub', category='planning', outputs=['product_vision']), capabilities=[AgentCapability(name='pv', description='stub')])

    def _execute(self, context: ExecutionContext):
        return [self.create_artifact(context, 'product_vision', '# Vision', DocumentArtifact)]


class _RequirementsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(metadata=AgentMetadata(name='requirements_agent', version='1.0.0', description='stub', category='planning', outputs=['requirements']), capabilities=[AgentCapability(name='req', description='stub')])

    def _execute(self, context: ExecutionContext):
        return [self.create_artifact(context, 'requirements', '# Requirements', DocumentArtifact)]


def _build_engine(tmp_path: Path) -> tuple[WorkflowEngine, WorkflowPersistence]:
    registry = AgentRegistry()
    registry.register(_VisionAgent())
    registry.register(_RequirementsAgent())
    executor = StepExecutor(registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
    persistence = WorkflowPersistence(tmp_path / 'state.json')
    engine = WorkflowEngine(
        Path('workflow/recipes'),
        WorkflowParser(WorkflowValidator()),
        executor,
        persistence=persistence,
    )
    return engine, persistence


# ---------------------------------------------------------------------------
# WorkflowPersistence unit tests
# ---------------------------------------------------------------------------

class TestWorkflowPersistence:
    def test_creates_store_file_on_init(self, tmp_path: Path) -> None:
        store = tmp_path / 'state.json'
        WorkflowPersistence(store)
        assert store.exists()
        assert json.loads(store.read_text()) == {}

    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        engine, persistence = _build_engine(tmp_path)
        instance = engine.run('requirements-gathering', project_id='p1')
        loaded = persistence.load(instance.run_id)
        assert loaded is not None
        assert loaded.run_id == instance.run_id
        assert loaded.status == 'succeeded'

    def test_load_unknown_run_id_returns_none(self, tmp_path: Path) -> None:
        persistence = WorkflowPersistence(tmp_path / 'state.json')
        assert persistence.load('nonexistent-id') is None

    def test_list_runs_returns_run_ids(self, tmp_path: Path) -> None:
        engine, persistence = _build_engine(tmp_path)
        r1 = engine.run('requirements-gathering', project_id='p1')
        r2 = engine.run('requirements-gathering', project_id='p2')
        runs = persistence.list_runs()
        assert r1.run_id in runs
        assert r2.run_id in runs

    def test_step_status_preserved(self, tmp_path: Path) -> None:
        engine, persistence = _build_engine(tmp_path)
        instance = engine.run('requirements-gathering', project_id='p1')
        loaded = persistence.load(instance.run_id)
        assert all(si.status == StepStatus.SUCCEEDED for si in loaded.step_instances)


# ---------------------------------------------------------------------------
# WorkflowEngine persistence integration tests
# ---------------------------------------------------------------------------

class TestWorkflowEngineWithPersistence:
    def test_run_saves_instance(self, tmp_path: Path) -> None:
        engine, persistence = _build_engine(tmp_path)
        instance = engine.run('requirements-gathering')
        assert instance.run_id in persistence.list_runs()

    def test_run_id_included_in_result(self, tmp_path: Path) -> None:
        engine, _ = _build_engine(tmp_path)
        instance = engine.run('requirements-gathering')
        assert instance.run_id  # non-empty string

    def test_engine_without_persistence_still_works(self) -> None:
        registry = AgentRegistry()
        registry.register(_VisionAgent())
        registry.register(_RequirementsAgent())
        executor = StepExecutor(registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
        engine = WorkflowEngine(Path('workflow/recipes'), WorkflowParser(WorkflowValidator()), executor)
        instance = engine.run('requirements-gathering')
        assert instance.status == 'succeeded'

    def test_resume_raises_without_persistence(self) -> None:
        engine = WorkflowEngine(Path('workflow/recipes'), WorkflowParser(WorkflowValidator()), MagicMock())
        with pytest.raises(RuntimeError, match='persistence'):
            engine.resume('some-run-id')

    def test_resume_raises_for_unknown_run_id(self, tmp_path: Path) -> None:
        engine, _ = _build_engine(tmp_path)
        with pytest.raises(KeyError):
            engine.resume('does-not-exist')

    def test_resume_skips_already_succeeded_steps(self, tmp_path: Path) -> None:
        """Mark the first step as succeeded before resuming; only second step runs."""
        engine, persistence = _build_engine(tmp_path)
        # Start a fresh run and immediately save with only the first step succeeded.
        instance = engine.run('requirements-gathering')
        # Simulate partial completion: reset second step to pending.
        for si in instance.step_instances:
            if si.definition.name == 'requirements':
                si.status = StepStatus.PENDING
                si.attempts = 0
                si.artifacts.clear()
        instance.artifacts = [a for a in instance.artifacts if a.name != 'requirements']
        instance.status = 'running'
        persistence.save(instance)

        resumed = engine.resume(instance.run_id)
        assert resumed.status == 'succeeded'
        names = [a.name for a in resumed.artifacts]
        assert 'requirements' in names


# ---------------------------------------------------------------------------
# WorkflowInstance model tests
# ---------------------------------------------------------------------------

class TestWorkflowInstanceModel:
    def test_run_id_auto_generated(self, tmp_path: Path) -> None:
        engine, _ = _build_engine(tmp_path)
        i1 = engine.run('requirements-gathering')
        i2 = engine.run('requirements-gathering')
        assert i1.run_id != i2.run_id


# ---------------------------------------------------------------------------
# CLI tests for resume command
# ---------------------------------------------------------------------------

class TestResumeCLI:
    def test_resume_parser_accepts_run_id(self) -> None:
        from cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(['resume', 'abc-123'])
        assert args.command == 'resume'
        assert args.run_id == 'abc-123'

    def test_resume_parser_accepts_optional_metadata(self) -> None:
        from cli.main import build_parser
        parser = build_parser()
        args = parser.parse_args(['resume', 'abc-123', '--idea', 'My app', '--platform', 'web'])
        assert args.idea == 'My app'
        assert args.platform == 'web'

    def test_build_output_includes_run_id(self) -> None:
        import json
        from unittest.mock import MagicMock, patch
        from cli.main import main
        fake_slugger = MagicMock()
        result = MagicMock()
        result.run_id = 'test-run-id-123'
        result.definition.name = 'full-sdlc'
        result.status = 'succeeded'
        result.artifacts = []
        fake_slugger.build.return_value = result
        with patch('cli.main.Bootstrap'), patch('cli.main.Slugger', return_value=fake_slugger):
            from io import StringIO
            import sys
            captured = []

            class _Cap:
                def write(self, s):
                    captured.append(s)
                def flush(self):
                    pass

            old_stdout = sys.stdout
            sys.stdout = _Cap()
            try:
                rc = main(['build', 'An idea', '--platform', 'web'])
            finally:
                sys.stdout = old_stdout
            output = json.loads(''.join(captured))
            assert rc == 0
            assert output['run_id'] == 'test-run-id-123'
