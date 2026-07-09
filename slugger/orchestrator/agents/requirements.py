"""Requirements agent.

This agent accepts a user request and produces a structured requirements
document using the configured AI provider. It stores the output in memory
and returns artifact metadata.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class RequirementsAgent(Agent):
    name = "requirements"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Produce requirements from a user request.

        Expects inputs:
        - request: The user's request or problem statement
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The structured requirements document
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        request = inputs.get("request", "")
        provider = inputs.get("_provider")

        if not request:
            return {"status": "error", "message": "No request provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a requirements analyst. Analyze the following user request and produce
a structured requirements document with sections: Overview, Functional Requirements, Non-Functional Requirements,
Assumptions, and Out of Scope.

User Request:
{request}

Provide the requirements document:"""

        result = provider.generate(prompt)
        requirements_text = result.get("response", "")

        return {
            "artifact": {
                "type": "requirements",
                "content": requirements_text,
                "source_request": request,
            },
            "artifact_name": "requirements_v1",
            "status": "success",
        }
