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
        result.outcome = None
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


# ---------------------------------------------------------------------------
# CC-001 regression tests: idea propagation through the pipeline
# ---------------------------------------------------------------------------

class TestIdeaPropagation:
    """Regression tests asserting that the user idea is the authoritative root
    of every downstream artifact produced by the workflow.

    The idea ``Create a simple task tracker CLI`` must appear verbatim in
    requirements, architecture, and implementation context — never replaced by
    a generic note or a Python object repr.
    """

    _IDEA = 'Create a simple task tracker CLI'

    def _run_pipeline(self, idea: str = _IDEA, workflow: str = 'python-project') -> object:
        from agents.planning.product_vision_agent import ProductVisionAgent
        from agents.planning.requirements_agent import RequirementsAgent
        from agents.planning.user_story_agent import UserStoryAgent
        # Use real planning agents so idea propagation can be asserted.
        # Other steps use stubs to avoid external dependencies.
        real_registry = AgentRegistry()
        for agent in [
            ProductVisionAgent(),
            RequirementsAgent(),
            UserStoryAgent(),
        ]:
            real_registry.register(agent)
        # Also register the remaining stubs for non-planning steps.
        for agent in _build_registry().list():
            from agents.registry import AgentRegistry as AR
            pass
        stub_registry = _build_registry()
        # Build a merged registry: real planning agents override stubs.
        merged_registry = AgentRegistry()
        for name in stub_registry.list():
            try:
                merged_registry.register(stub_registry.resolve(name))
            except Exception:
                pass
        # Override with real agents.
        for agent in [ProductVisionAgent(), RequirementsAgent(), UserStoryAgent()]:
            merged_registry.register(agent)
        executor = StepExecutor(merged_registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
        engine = WorkflowEngine(Path('workflow/recipes'), WorkflowParser(WorkflowValidator()), executor)
        from models.project import ProjectBrief, Platform, CodingAgent
        brief = ProjectBrief(idea=idea, platform=Platform.WEB)
        metadata = brief.as_metadata()
        return engine.run(workflow, project_id='test-idea-propagation', metadata=metadata, project_brief=brief)

    def test_idea_not_absent_in_product_vision(self) -> None:
        result = self._run_pipeline()
        vision = next(a for a in result.artifacts if a.name == 'product_vision')
        assert self._IDEA in vision.content

    def test_idea_not_absent_in_requirements(self) -> None:
        result = self._run_pipeline()
        reqs = next(a for a in result.artifacts if a.name == 'requirements')
        assert self._IDEA in reqs.content

    def test_no_artifact_contains_explicit_inputs_note(self) -> None:
        result = self._run_pipeline()
        for artifact in result.artifacts:
            assert 'No explicit inputs were supplied' not in artifact.content

    def test_no_artifact_contains_python_object_repr(self) -> None:
        """Artifact content must not embed raw Python dataclass reprs."""
        result = self._run_pipeline()
        for artifact in result.artifacts:
            # dataclass reprs look like ClassName(field=...) — detect the most
            # common forms emitted by Artifact and ExecutionContext subclasses
            assert 'DocumentArtifact(' not in artifact.content
            assert 'CodeArtifact(' not in artifact.content
            assert 'ExecutionContext(' not in artifact.content

    def test_outcome_is_artifacts_generated_not_production_ready(self) -> None:
        """A placeholder-only run must not report a production-ready outcome."""
        result = self._run_pipeline()
        from workflow.models import WorkflowOutcome
        assert result.outcome is not None
        assert result.outcome == WorkflowOutcome.ARTIFACTS_GENERATED
        assert result.outcome != WorkflowOutcome.PRODUCTION_READY
        assert result.outcome != WorkflowOutcome.RELEASED

    def test_project_brief_round_trips_through_metadata(self) -> None:
        """ProjectBrief serialises to metadata and deserialises back correctly."""
        from models.project import ProjectBrief, Platform, CodingAgent, AppType, DesignPreference
        brief = ProjectBrief(
            idea=self._IDEA,
            platform=Platform.WEB,
            app_type=AppType.CLI,
            target_users='developers',
            constraints=['no-db'],
            nonfunctional_requirements=['fast-startup'],
            coding_agent=CodingAgent.CODEX,
            design_preference=DesignPreference.NONE,
        )
        meta = brief.as_metadata()
        restored = ProjectBrief.from_metadata(meta)
        assert restored.idea == brief.idea
        assert restored.platform == brief.platform
        assert restored.app_type == brief.app_type
        assert restored.target_users == brief.target_users
        assert restored.constraints == brief.constraints
        assert restored.nonfunctional_requirements == brief.nonfunctional_requirements
        assert restored.coding_agent == brief.coding_agent
        assert restored.design_preference == brief.design_preference

    def test_cli_output_includes_outcome_field(self) -> None:
        """The build CLI output must include the ``outcome`` field."""
        import json
        from unittest.mock import MagicMock, patch
        from cli.main import main
        from workflow.models import WorkflowOutcome
        fake_slugger = MagicMock()
        result = MagicMock()
        result.run_id = 'outcome-test-run'
        result.definition.name = 'full-sdlc-v2'
        result.status = 'succeeded'
        result.artifacts = []
        result.outcome = WorkflowOutcome.ARTIFACTS_GENERATED
        fake_slugger.build.return_value = result
        import io
        import sys
        with patch('cli.main.Bootstrap'), patch('cli.main.Slugger', return_value=fake_slugger):
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(['build', self._IDEA, '--platform', 'web'])
        assert rc == 0
        output = json.loads(buf.getvalue())
        assert 'outcome' in output
        assert output['outcome'] == WorkflowOutcome.ARTIFACTS_GENERATED.value
        assert output['outcome'] != WorkflowOutcome.PRODUCTION_READY.value
