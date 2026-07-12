"""CodeGeneratorAgent implementation."""

from __future__ import annotations

import logging
import textwrap
from pathlib import Path
from tempfile import mkdtemp

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.execution import ExecutionContext

_LOG = logging.getLogger(__name__)

_PLATFORM_NOTES: dict[str, str] = {
    'web': 'FastAPI web application with REST endpoints',
    'ios': 'Python back-end service powering an iOS application',
    'android': 'Python back-end service powering an Android application',
}

_AGENT_NOTES: dict[str, str] = {
    'codex': 'OpenAI Codex',
    'anthropic': 'Anthropic Claude',
}

def _escape_triple_quotes(text: str) -> str:
    """Escape triple-quote sequences so *text* is safe to embed in string literals.

    Both ``\"\"\"`` and ``'''`` are replaced with escaped equivalents to prevent
    either from prematurely closing a surrounding docstring or code block.
    """
    return (
        text
        .replace('"""', '\\"\\"\\"')
        .replace("'''", "\\'\\'\\'")
        .replace('\r', '')
        .strip()
    )


def _python_scaffold(idea: str, platform: str, coding_agent: str) -> str:
    """Return a Python project scaffold as a markdown-formatted code listing."""

    safe_idea = _escape_triple_quotes(idea)
    platform_note = _PLATFORM_NOTES.get(platform, platform)
    agent_note = _AGENT_NOTES.get(coding_agent, coding_agent)

    return textwrap.dedent(f"""\
        # Generated Python Project

        **Idea:** {safe_idea}
        **Platform:** {platform_note}
        **Coding agent:** {agent_note}

        ---

        ## Project Structure

        ```
        project/
        ├── README.md
        ├── pyproject.toml
        ├── src/
        │   └── app/
        │       ├── __init__.py
        │       └── main.py
        └── tests/
            ├── __init__.py
            └── test_main.py
        ```

        ---

        ## src/app/main.py

        ```python
        \"\"\"Entry point for: {safe_idea}.\"\"\"

        from __future__ import annotations


        def run() -> None:
            \"\"\"Run the application.\"\"\"
            print("Running: {safe_idea}")


        if __name__ == "__main__":
            run()
        ```

        ---

        ## tests/test_main.py

        ```python
        \"\"\"Smoke tests for: {safe_idea}.\"\"\"

        from app.main import run


        def test_run_executes_without_error() -> None:
            run()
        ```

        ---

        ## pyproject.toml

        ```toml
        [project]
        name = "project"
        version = "0.1.0"
        requires-python = ">=3.11"

        [project.optional-dependencies]
        test = ["pytest"]
        ```
    """)


class CodeGeneratorAgent(BaseAgent):
    """Create code artifacts.

    When a ``codex_agent_client`` is available in the execution context the
    agent delegates to the full coding-agent adapter (workspace-level file
    writes, command evidence).  When not available it falls back to the
    template scaffold so that all tests and offline runs continue to work.
    """

    def __init__(self) -> None:
        super().__init__(
            metadata=AgentMetadata(
                name='code_generator_agent',
                version='1.0.0',
                description='Create code artifacts.',
                category='development',
                inputs=[],
                outputs=['generated_code'],
                tags=['development', 'code_generation'],
                provider='mock',
                external_interface='openai_codex',
            ),
            capabilities=[AgentCapability(name='code_generation', description='Create code artifacts.', outputs=('generated_code',))],
        )

    def _execute(self, context: ExecutionContext):
        idea = context.get_idea() or 'Unspecified idea'
        platform = context.metadata.get('platform', 'web')
        if context.project_brief is not None:
            platform = context.project_brief.platform.value
        coding_agent = context.metadata.get('coding_agent', 'codex')
        if context.project_brief is not None:
            coding_agent = context.project_brief.coding_agent.value

        content = self._generate_code(idea, platform, coding_agent, context)
        return [self.create_artifact(context, 'generated_code', content, CodeArtifact)]

    def _generate_code(self, idea: str, platform: str, coding_agent: str, context: ExecutionContext) -> str:
        client = getattr(context, 'codex_agent_client', None)
        if client is not None:
            from providers.codex_agent_client import CodexWorkspace
            workspace = CodexWorkspace(root=Path(mkdtemp(prefix='slugger_codex_')))
            try:
                task_brief = f"Generate a complete {platform} application for: {idea}"
                result = client.start_task(task_brief, workspace)
                if result.success and result.file_changes:
                    # Assemble content from all file changes
                    parts = [f"# Generated by Codex Agent\n\n**Session:** {result.session_id}\n"]
                    for fc in result.file_changes:
                        parts.append(f"\n## {fc.path}\n\n```python\n{fc.content}\n```\n")
                    if result.commands_run:
                        parts.append(f"\n## Commands run\n\n" + '\n'.join(f'- `{c}`' for c in result.commands_run))
                    return '\n'.join(parts)
            except Exception as exc:  # noqa: BLE001
                _LOG.warning('Codex agent code generation failed, using scaffold: %s', exc)

        return _python_scaffold(idea, platform, coding_agent)
