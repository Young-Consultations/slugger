"""CodeGeneratorAgent implementation."""

from __future__ import annotations

import textwrap

from agents.base import BaseAgent
from models.agent import AgentCapability, AgentMetadata
from models.artifact import CodeArtifact
from models.execution import ExecutionContext

_PLATFORM_NOTES: dict[str, str] = {
    'web': 'FastAPI web application with REST endpoints',
    'ios': 'Python back-end service powering an iOS application',
    'android': 'Python back-end service powering an Android application',
}

_AGENT_NOTES: dict[str, str] = {
    'codex': 'OpenAI Codex',
    'anthropic': 'Anthropic Claude',
}

_SAFE_CHARS_RE = None


def _sanitize_for_docstring(text: str) -> str:
    """Strip characters that could break a Python docstring or markdown block."""
    # Replace triple-quotes to avoid prematurely closing the docstring.
    return text.replace('"""', "'''").replace('\r', '').strip()


def _python_scaffold(idea: str, platform: str, coding_agent: str) -> str:
    """Return a Python project scaffold as a markdown-formatted code listing."""

    safe_idea = _sanitize_for_docstring(idea)
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
    """Create code artifacts."""

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
        idea = context.metadata.get('idea', 'Unspecified idea')
        platform = context.metadata.get('platform', 'web')
        coding_agent = context.metadata.get('coding_agent', 'codex')
        content = _python_scaffold(idea, platform, coding_agent)
        return [self.create_artifact(context, 'generated_code', content, CodeArtifact)]
