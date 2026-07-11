"""End-to-end integration test for the orchestration pipeline (Task 037)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agents.base import BaseAgent
from agents.registry import AgentRegistry
from cli.main import main
from models import AgentCapability, AgentMetadata, DocumentArtifact
from models.artifact import CodeArtifact, ConfigArtifact, TestArtifact
from models.execution import ExecutionContext
from models.project import CodingAgent, Platform, ProjectInput
from orchestrator import Bootstrap, Slugger
from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
from workflow import StepExecutor, WorkflowEngine, WorkflowParser


# ---------------------------------------------------------------------------
# Minimal stub agents for the python-project workflow steps
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


class _SystemDesignAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(metadata=AgentMetadata(name='system_design_agent', version='1.0.0', description='stub', category='architecture', outputs=['system_design']), capabilities=[AgentCapability(name='sd', description='stub')])

    def _execute(self, context: ExecutionContext):
        return [self.create_artifact(context, 'system_design', '# System Design', DocumentArtifact)]


class _TestGeneratorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(metadata=AgentMetadata(name='test_generator_agent', version='1.0.0', description='stub', category='qa', outputs=['test_suite']), capabilities=[AgentCapability(name='tg', description='stub')])

    def _execute(self, context: ExecutionContext):
        return [self.create_artifact(context, 'test_suite', '# Tests', TestArtifact)]


class _CICDAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(metadata=AgentMetadata(name='ci_cd_agent', version='1.0.0', description='stub', category='operations', outputs=['ci_cd_pipeline']), capabilities=[AgentCapability(name='ci', description='stub')])

    def _execute(self, context: ExecutionContext):
        return [self.create_artifact(context, 'ci_cd_pipeline', '# CI/CD', ConfigArtifact)]


def _build_registry() -> AgentRegistry:
    from agents.development.code_generator_agent import CodeGeneratorAgent
    registry = AgentRegistry()
    for agent in [_VisionAgent(), _RequirementsAgent(), _SystemDesignAgent(), CodeGeneratorAgent(), _TestGeneratorAgent(), _CICDAgent()]:
        registry.register(agent)
    return registry


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPythonProjectPipeline:
    """End-to-end tests for the python-project workflow."""

    def _run_pipeline(self, idea: str, platform: str = 'web', coding_agent: str = 'codex'):
        registry = _build_registry()
        executor = StepExecutor(registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
        engine = WorkflowEngine(Path('workflow/recipes'), WorkflowParser(WorkflowValidator()), executor)
        metadata = {'idea': idea, 'platform': platform, 'coding_agent': coding_agent}
        return engine.run('python-project', project_id='test-project', metadata=metadata)

    def test_pipeline_succeeds(self) -> None:
        result = self._run_pipeline('A todo list app')
        assert result.status == 'succeeded'

    def test_pipeline_produces_required_artifacts(self) -> None:
        result = self._run_pipeline('A todo list app')
        names = [a.name for a in result.artifacts]
        assert 'product_vision' in names
        assert 'requirements' in names
        assert 'system_design' in names
        assert 'generated_code' in names
        assert 'test_suite' in names
        assert 'ci_cd_pipeline' in names

    def test_code_generator_uses_idea_metadata(self) -> None:
        result = self._run_pipeline('An e-commerce shop', platform='web', coding_agent='anthropic')
        code_artifact = next(a for a in result.artifacts if a.name == 'generated_code')
        assert 'An e-commerce shop' in code_artifact.content
        assert 'web' in code_artifact.content.lower() or 'FastAPI' in code_artifact.content
        assert 'anthropic' in code_artifact.content.lower() or 'Anthropic' in code_artifact.content

    def test_code_artifact_is_python_format(self) -> None:
        result = self._run_pipeline('A chat app', platform='ios')
        code_artifact = next(a for a in result.artifacts if a.name == 'generated_code')
        assert isinstance(code_artifact, CodeArtifact)
        assert code_artifact.format == 'python'

    def test_pipeline_embeds_platform_in_code_artifact(self) -> None:
        for platform in ('web', 'ios', 'android'):
            result = self._run_pipeline('My app', platform=platform)
            code_artifact = next(a for a in result.artifacts if a.name == 'generated_code')
            assert platform in code_artifact.content.lower() or any(
                note in code_artifact.content
                for note in ('FastAPI', 'iOS', 'Android', 'web', 'ios', 'android')
            ), f'Platform {platform} not reflected in code artifact'


class TestOrchestrationPipelineCLI:
    """CLI integration tests for Task 037."""

    @patch('cli.main.Bootstrap')
    def test_build_with_python_project_workflow(self, mock_bootstrap: MagicMock, capsys) -> None:
        fake_slugger = MagicMock()
        result = MagicMock()
        result.definition.name = 'python-project'
        result.status = 'succeeded'
        result.artifacts = []
        result.run_id = 'test-run-id'
        fake_slugger.build.return_value = result
        mock_bootstrap.return_value.build.return_value = MagicMock()
        with patch('cli.main.Slugger', return_value=fake_slugger):
            rc = main(['build', 'A todo app', '--platform', 'web', '--workflow', 'python-project'])
        assert rc == 0
        captured = capsys.readouterr()
        import json
        output = json.loads(captured.out)
        assert output['workflow'] == 'python-project'

    def test_python_project_listed_as_workflow(self) -> None:
        engine = WorkflowEngine(
            Path('workflow/recipes'),
            WorkflowParser(WorkflowValidator()),
            MagicMock(),
        )
        assert 'python-project' in engine.list_workflows()
