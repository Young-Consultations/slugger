"""CC-005: Codex coding-agent adapter tests."""

from __future__ import annotations

from pathlib import Path
from tempfile import mkdtemp

import pytest

from providers.codex_agent_client import (
    CodexEvent,
    CodexEventType,
    CodexTaskResult,
    CodexWorkspace,
    FakeCodexAgentClient,
    FileChange,
    ICodexAgentClient,
    ReviewFinding,
)


# ---------------------------------------------------------------------------
# FakeCodexAgentClient tests
# ---------------------------------------------------------------------------

class TestFakeCodexAgentClient:
    def test_start_task_returns_success(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        result = client.start_task('Build a hello-world app', workspace)
        assert result.success is True
        assert result.session_id
        assert len(result.file_changes) == 1

    def test_start_task_records_call(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        client.start_task('test task', workspace)
        assert any(c['method'] == 'start_task' for c in client.calls)

    def test_start_task_accepts_explicit_session_id(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        result = client.start_task('task', workspace, session_id='my-session')
        assert result.session_id == 'my-session'

    def test_continue_task_returns_success(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        result = client.continue_task('existing-session', 'Add error handling', workspace)
        assert result.success is True

    def test_review_returns_findings(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        result = client.review('def foo(): pass', language='Python')
        assert len(result.findings) >= 1
        for finding in result.findings:
            assert finding.severity in ('critical', 'high', 'medium', 'low', 'info')

    def test_review_records_events(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        result = client.review('def foo(): pass')
        events = client.retrieve_events(result.session_id)
        assert any(e.event_type == CodexEventType.REVIEW_FINDING for e in events)

    def test_terminate_removes_session(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        result = client.start_task('task', workspace)
        sid = result.session_id
        client.terminate(sid)
        assert client.retrieve_events(sid) == []

    def test_multiple_tasks_have_distinct_sessions(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        r1 = client.start_task('task1', workspace)
        r2 = client.start_task('task2', workspace)
        assert r1.session_id != r2.session_id

    def test_custom_code_in_file_changes(self, tmp_path: Path) -> None:
        custom_code = 'def main():\n    return 42\n'
        client = FakeCodexAgentClient(default_code=custom_code)
        workspace = CodexWorkspace(root=tmp_path)
        result = client.start_task('task', workspace)
        assert result.file_changes[0].content == custom_code

    def test_custom_findings_in_review(self) -> None:
        findings = [ReviewFinding(severity='high', message='Missing type hints')]
        client = FakeCodexAgentClient(default_findings=findings)
        result = client.review('def foo(x): return x')
        assert result.findings[0].severity == 'high'
        assert 'type hints' in result.findings[0].message


# ---------------------------------------------------------------------------
# CodexWorkspace safety tests
# ---------------------------------------------------------------------------

class TestCodexWorkspace:
    def test_path_within_root_is_allowed(self, tmp_path: Path) -> None:
        ws = CodexWorkspace(root=tmp_path)
        assert ws.is_path_allowed(str(tmp_path / 'src' / 'main.py')) is True

    def test_path_outside_root_is_denied(self, tmp_path: Path) -> None:
        ws = CodexWorkspace(root=tmp_path)
        assert ws.is_path_allowed('/etc/passwd') is False

    def test_explicit_allow_list_checked(self, tmp_path: Path) -> None:
        ws = CodexWorkspace(root=tmp_path, write_allowed_paths=[str(tmp_path / 'src')])
        assert ws.is_path_allowed(str(tmp_path / 'src' / 'app.py')) is True
        assert ws.is_path_allowed(str(tmp_path / 'docs' / 'readme.md')) is False

    def test_allowed_command(self, tmp_path: Path) -> None:
        ws = CodexWorkspace(root=tmp_path)
        assert ws.is_command_allowed('python main.py') is True
        assert ws.is_command_allowed('rm -rf /') is False

    def test_custom_allowed_commands(self, tmp_path: Path) -> None:
        ws = CodexWorkspace(root=tmp_path, allowed_commands=['make'])
        assert ws.is_command_allowed('make test') is True
        assert ws.is_command_allowed('python test.py') is False


# ---------------------------------------------------------------------------
# CodeGeneratorAgent uses Codex client
# ---------------------------------------------------------------------------

class TestCodeGeneratorWithCodexClient:
    def test_uses_codex_client_when_available(self, tmp_path: Path) -> None:
        from agents.development.code_generator_agent import CodeGeneratorAgent
        from models.execution import ExecutionContext

        client = FakeCodexAgentClient(default_code='print("from codex")\n')
        ctx = ExecutionContext(
            project_id='p1',
            workflow_name='wf',
            step_name='step',
            metadata={'idea': 'hello world app'},
        )
        ctx.codex_agent_client = client  # inject via __dict__ (slots=True uses dict-based attrs)
        agent = CodeGeneratorAgent()
        artifacts = agent.execute(ctx)
        assert len(artifacts) == 1
        content = artifacts[0].content
        assert 'from codex' in content
        assert any(c['method'] == 'start_task' for c in client.calls)

    def test_falls_back_without_codex_client(self) -> None:
        from agents.development.code_generator_agent import CodeGeneratorAgent
        from models.execution import ExecutionContext

        ctx = ExecutionContext(
            project_id='p1',
            workflow_name='wf',
            step_name='step',
            metadata={'idea': 'hello world app'},
        )
        artifacts = CodeGeneratorAgent().execute(ctx)
        assert 'Generated Python Project' in artifacts[0].content

    def test_falls_back_on_codex_client_error(self, tmp_path: Path) -> None:
        from agents.development.code_generator_agent import CodeGeneratorAgent
        from models.execution import ExecutionContext
        from unittest.mock import MagicMock

        client = MagicMock()
        client.start_task.side_effect = RuntimeError('codex crashed')
        ctx = ExecutionContext(
            project_id='p1',
            workflow_name='wf',
            step_name='step',
            metadata={'idea': 'hello world app'},
        )
        ctx.codex_agent_client = client
        artifacts = CodeGeneratorAgent().execute(ctx)
        # Should fall back to scaffold, not raise
        assert 'Generated Python Project' in artifacts[0].content


# ---------------------------------------------------------------------------
# ICodexAgentClient abstract contract enforced
# ---------------------------------------------------------------------------

class TestICodexAgentClientContract:
    def test_fake_implements_interface(self) -> None:
        assert issubclass(FakeCodexAgentClient, ICodexAgentClient)

    def test_fake_is_instantiable(self) -> None:
        client = FakeCodexAgentClient()
        assert client is not None

    def test_codex_task_result_has_required_fields(self, tmp_path: Path) -> None:
        client = FakeCodexAgentClient()
        workspace = CodexWorkspace(root=tmp_path)
        result = client.start_task('task', workspace)
        assert hasattr(result, 'session_id')
        assert hasattr(result, 'success')
        assert hasattr(result, 'file_changes')
        assert hasattr(result, 'commands_run')
        assert hasattr(result, 'findings')
        assert hasattr(result, 'summary')
