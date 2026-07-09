"""Coding agent.

This agent accepts a project plan and architecture design, and generates
source code scaffolds and project structure based on the technology stack
recommendations.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class CodingAgent(Agent):
    name = "coding"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate source code scaffolds from plan and architecture.

        Expects inputs:
        - artifact: (optional) The project plan artifact from a prior step
        - plan_text: (optional) Raw project plan text
        - architecture_text: (optional) Raw architecture text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The code scaffolds and project structure
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract plan or architecture from artifact or raw text
        context_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            context_text = inputs["artifact"].get("content", "")
        if not context_text:
            context_text = inputs.get("plan_text", "")
        if not context_text:
            context_text = inputs.get("architecture_text", "")

        if not context_text:
            return {"status": "error", "message": "No plan or architecture provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a senior software architect and code generator. Based on the following project plan
and architecture design, generate source code scaffolds and project structure including:

1. **Project Structure** — Directory layout and file organization
2. **Technology Stack Setup** — Package managers, dependencies, configuration files
3. **Core Modules** — Main application files with boilerplate code
4. **API/Controller Layer** — Endpoint definitions and request handlers
5. **Service Layer** — Business logic service classes
6. **Data Access Layer** — Database models and repository patterns
7. **Configuration** — Environment configs, feature flags, settings
8. **Utilities** — Helper functions, logging, error handling
9. **Entry Point** — Main application startup file
10. **Build/Deploy Scripts** — Makefile, Docker setup, CI/CD hooks

For each major component, provide:
- File path and name
- Code skeleton (imports, class/function signatures, docstrings)
- Key implementation notes and TODOs

Project Plan & Architecture:
{context_text}

Generate the complete code scaffold:"""

        result = provider.generate(prompt)
        code_scaffold = result.get("response", "")

        return {
            "artifact": {
                "type": "code_scaffold",
                "content": code_scaffold,
            },
            "artifact_name": "code_scaffold_v1",
            "status": "success",
        }
