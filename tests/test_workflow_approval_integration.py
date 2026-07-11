"""Tests for Epic 4: approval policy in workflow models and engine (WP-022, WP-023)."""

from __future__ import annotations

import pytest

from workflow.models import ApprovalPolicy, WorkflowStepDefinition


# ---------------------------------------------------------------------------
# ApprovalPolicy model
# ---------------------------------------------------------------------------


class TestApprovalPolicy:
    def test_defaults(self) -> None:
        policy = ApprovalPolicy()
        assert policy.required_approvers == []
        assert policy.auto_approve is False
        assert policy.timeout_seconds == 3600
        assert policy.on_timeout == 'abort'
        assert policy.quorum == 0

    def test_from_dict_full(self) -> None:
        data = {
            'required_approvers': ['alice', 'bob'],
            'auto_approve': True,
            'timeout_seconds': 7200,
            'on_timeout': 'escalate',
            'quorum': 1,
        }
        policy = ApprovalPolicy.from_dict(data)
        assert policy.required_approvers == ['alice', 'bob']
        assert policy.auto_approve is True
        assert policy.timeout_seconds == 7200
        assert policy.on_timeout == 'escalate'
        assert policy.quorum == 1

    def test_from_dict_empty(self) -> None:
        policy = ApprovalPolicy.from_dict({})
        assert policy.auto_approve is False
        assert policy.timeout_seconds == 3600


class TestWorkflowStepDefinitionApprovalPolicy:
    def test_step_defaults_to_no_approval_policy(self) -> None:
        step = WorkflowStepDefinition(name='build', agent='code_generator_agent')
        assert step.approval_policy is None

    def test_step_with_auto_approve_policy(self) -> None:
        policy = ApprovalPolicy(auto_approve=True)
        step = WorkflowStepDefinition(
            name='deploy',
            agent='deployment_agent',
            approval_policy=policy,
        )
        assert step.approval_policy is not None
        assert step.approval_policy.auto_approve is True


# ---------------------------------------------------------------------------
# WorkflowEngine approval gate integration
# ---------------------------------------------------------------------------


class TestWorkflowEngineApprovalGate:
    """Verify that auto_approve gates allow execution to proceed."""

    def test_auto_approve_does_not_block_execution(self, tmp_path) -> None:
        import yaml

        from agents.base import BaseAgent
        from agents.registry import AgentRegistry
        from models import AgentCapability, AgentMetadata, DocumentArtifact
        from models.artifact_store import InMemoryArtifactStore
        from models.execution import ExecutionContext
        from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
        from workflow import StepExecutor, WorkflowEngine, WorkflowParser

        recipe = {
            'name': 'approval-test',
            'version': '1.0',
            'steps': [
                {
                    'name': 'vision_step',
                    'agent': 'vision_agent',
                    'outputs': ['product_vision'],
                    'approval_policy': {
                        'auto_approve': True,
                        'required_approvers': [],
                    },
                }
            ],
        }
        recipe_dir = tmp_path / 'recipes'
        recipe_dir.mkdir()
        (recipe_dir / 'approval-test.yaml').write_text(yaml.dump(recipe), encoding='utf-8')

        class VisionAgent(BaseAgent):
            def __init__(self) -> None:
                super().__init__(
                    metadata=AgentMetadata(
                        name='vision_agent', version='1.0.0', description='stub',
                        category='planning', outputs=['product_vision'],
                    ),
                    capabilities=[AgentCapability(name='pv', description='stub')],
                )

            def _execute(self, context: ExecutionContext):
                return [self.create_artifact(context, 'product_vision', '# Vision', DocumentArtifact)]

        registry = AgentRegistry()
        registry.register(VisionAgent())
        executor = StepExecutor(registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
        store = InMemoryArtifactStore()
        engine = WorkflowEngine(recipe_dir, WorkflowParser(WorkflowValidator()), executor, store)
        instance = engine.run('approval-test', project_id='test-proj')
        assert instance.status == 'succeeded'

    def test_non_auto_approve_pauses_execution(self, tmp_path) -> None:
        """A non-auto-approve gate pauses the workflow (awaiting_approval status)."""
        import yaml

        from agents.base import BaseAgent
        from agents.registry import AgentRegistry
        from models import AgentCapability, AgentMetadata, DocumentArtifact
        from models.artifact_store import InMemoryArtifactStore
        from models.execution import ExecutionContext
        from validators import ArtifactValidator, QualityGateEvaluator, WorkflowValidator
        from workflow import StepExecutor, WorkflowEngine, WorkflowParser

        recipe = {
            'name': 'approval-pause-test',
            'version': '1.0',
            'steps': [
                {
                    'name': 'protected_step',
                    'agent': 'vision_agent',
                    'outputs': ['product_vision'],
                    'approval_policy': {
                        'auto_approve': False,
                        'required_approvers': ['alice'],
                    },
                }
            ],
        }
        recipe_dir = tmp_path / 'recipes'
        recipe_dir.mkdir()
        (recipe_dir / 'approval-pause-test.yaml').write_text(yaml.dump(recipe), encoding='utf-8')

        class VisionAgent(BaseAgent):
            def __init__(self) -> None:
                super().__init__(
                    metadata=AgentMetadata(
                        name='vision_agent', version='1.0.0', description='stub',
                        category='planning', outputs=['product_vision'],
                    ),
                    capabilities=[AgentCapability(name='pv', description='stub')],
                )

            def _execute(self, context: ExecutionContext):
                return [self.create_artifact(context, 'product_vision', '# Vision', DocumentArtifact)]

        registry = AgentRegistry()
        registry.register(VisionAgent())
        executor = StepExecutor(registry, QualityGateEvaluator({'artifact_validator': ArtifactValidator()}))
        engine = WorkflowEngine(recipe_dir, WorkflowParser(WorkflowValidator()), executor)
        instance = engine.run('approval-pause-test', project_id='test-proj')
        assert instance.status == 'awaiting_approval'
