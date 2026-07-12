"""CC-004: ChatGPT-backed planning agents and prompt review tests."""

from __future__ import annotations

from models.artifact import DocumentArtifact
from models.execution import ExecutionContext
from services.chatgpt import MockChatGPTService


def _make_context(idea: str = 'test idea', chatgpt_service=None, **extra_inputs) -> ExecutionContext:
    ctx = ExecutionContext(
        project_id='p1',
        workflow_name='wf',
        step_name='step',
        inputs=extra_inputs,
        metadata={'idea': idea},
        chatgpt_service=chatgpt_service,
    )
    return ctx


class TestProductVisionWithChatGPT:
    def test_uses_chatgpt_when_available(self):
        from agents.planning.product_vision_agent import ProductVisionAgent
        svc = MockChatGPTService(default_response='AI-generated vision content')
        ctx = _make_context(idea='Build a task manager', chatgpt_service=svc)
        agent = ProductVisionAgent()
        artifacts = agent.execute(ctx)
        assert len(artifacts) == 1
        assert 'AI-generated vision content' in artifacts[0].content
        assert len(svc.calls) == 1
        assert svc.calls[0]['type'] == 'execute'

    def test_falls_back_when_chatgpt_unavailable(self):
        from agents.planning.product_vision_agent import ProductVisionAgent
        ctx = _make_context(idea='Build a task manager', chatgpt_service=None)
        agent = ProductVisionAgent()
        artifacts = agent.execute(ctx)
        assert len(artifacts) == 1
        assert 'Product Vision' in artifacts[0].content
        assert 'task manager' in artifacts[0].content

    def test_falls_back_on_chatgpt_exception(self):
        from agents.planning.product_vision_agent import ProductVisionAgent
        from unittest.mock import MagicMock
        svc = MagicMock()
        svc.execute.side_effect = RuntimeError('network error')
        ctx = _make_context(idea='Build a task manager', chatgpt_service=svc)
        agent = ProductVisionAgent()
        # Should not raise; falls back to template
        artifacts = agent.execute(ctx)
        assert len(artifacts) == 1
        assert 'Product Vision' in artifacts[0].content

    def test_prompt_contains_idea(self):
        from agents.planning.product_vision_agent import ProductVisionAgent
        svc = MockChatGPTService()
        ctx = _make_context(idea='social recipe sharing app', chatgpt_service=svc)
        ProductVisionAgent().execute(ctx)
        assert 'social recipe sharing app' in svc.calls[0]['prompt']


class TestRequirementsWithChatGPT:
    def test_uses_chatgpt_when_available(self):
        from agents.planning.requirements_agent import RequirementsAgent
        from models.artifact import DocumentArtifact
        svc = MockChatGPTService(default_response='REQ-001: The system shall...')
        ctx = _make_context(idea='task manager', chatgpt_service=svc)
        artifacts = RequirementsAgent().execute(ctx)
        assert 'REQ-001' in artifacts[0].content

    def test_includes_vision_in_prompt(self):
        from agents.planning.requirements_agent import RequirementsAgent
        from models.artifact import DocumentArtifact
        svc = MockChatGPTService()
        vision = DocumentArtifact(artifact_id='a1', name='product_vision', content='# Vision\nGreat app')
        ctx = _make_context(idea='task manager', chatgpt_service=svc)
        ctx.inputs['product_vision'] = vision
        RequirementsAgent().execute(ctx)
        prompt_text = svc.calls[0]['prompt']
        assert 'Great app' in prompt_text

    def test_falls_back_without_service(self):
        from agents.planning.requirements_agent import RequirementsAgent
        ctx = _make_context(idea='task manager', chatgpt_service=None)
        artifacts = RequirementsAgent().execute(ctx)
        assert 'Requirements' in artifacts[0].content


class TestUserStoryWithChatGPT:
    def test_uses_chatgpt_when_available(self):
        from agents.planning.user_story_agent import UserStoryAgent
        svc = MockChatGPTService(default_response='As a user, I want to...')
        ctx = _make_context(idea='task manager', chatgpt_service=svc)
        artifacts = UserStoryAgent().execute(ctx)
        assert 'As a user' in artifacts[0].content

    def test_falls_back_without_service(self):
        from agents.planning.user_story_agent import UserStoryAgent
        ctx = _make_context(idea='task manager')
        artifacts = UserStoryAgent().execute(ctx)
        assert 'User Stories' in artifacts[0].content


class TestProjectPlanWithChatGPT:
    def test_uses_chatgpt_when_available(self):
        from agents.planning.project_plan_agent import ProjectPlanAgent
        svc = MockChatGPTService(default_response='Sprint 1: Setup...')
        ctx = _make_context(idea='task manager', chatgpt_service=svc)
        artifacts = ProjectPlanAgent().execute(ctx)
        assert 'Sprint 1' in artifacts[0].content

    def test_falls_back_without_service(self):
        from agents.planning.project_plan_agent import ProjectPlanAgent
        ctx = _make_context(idea='task manager')
        artifacts = ProjectPlanAgent().execute(ctx)
        assert 'Project Plan' in artifacts[0].content


class TestPromptReviewIntegration:
    def test_mock_service_review_passes(self):
        svc = MockChatGPTService()
        result = svc.review_prompt('Write requirements for a task manager app.')
        assert result.passed is True
        assert result.score > 0
        assert result.feedback

    def test_mock_service_review_has_suggestions(self):
        svc = MockChatGPTService()
        result = svc.review_prompt('Write requirements for a task manager app.')
        assert isinstance(result.suggestions, list)

    def test_review_prompt_logged_in_calls(self):
        svc = MockChatGPTService()
        svc.review_prompt('some prompt')
        assert any(c['type'] == 'review' for c in svc.calls)


class TestStepExecutorPassesChatGPT:
    def test_executor_injects_chatgpt_into_context(self):
        """StepExecutor should pass chatgpt_service to ExecutionContext."""
        from unittest.mock import MagicMock
        from workflow.executor import StepExecutor
        from workflow.models import WorkflowStepDefinition, StepInstance
        from validators import QualityGateEvaluator, ArtifactValidator

        svc = MockChatGPTService()
        captured_contexts = []

        class CapturingAgent:
            metadata = MagicMock()
            metadata.name = 'test_agent'

            def execute(self, context):
                captured_contexts.append(context)
                return []

        registry = MagicMock()
        registry.resolve.return_value = CapturingAgent()

        step_def = WorkflowStepDefinition(name='step', agent='test_agent', inputs=[], outputs=[], quality_gates=[])
        step_inst = StepInstance(definition=step_def)

        executor = StepExecutor(
            agent_registry=registry,
            quality_gate_evaluator=QualityGateEvaluator({'artifact_validator': ArtifactValidator()}),
            chatgpt_service=svc,
        )
        executor.execute('wf', 'p1', step_inst, {})
        assert len(captured_contexts) == 1
        assert captured_contexts[0].chatgpt_service is svc
