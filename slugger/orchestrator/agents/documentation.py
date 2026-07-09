"""Documentation agent.

This agent accepts code, architecture, and requirements, and generates
comprehensive project documentation including API docs, guides, and deployment docs.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class DocumentationAgent(Agent):
    name = "documentation"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive documentation from code and architecture.

        Expects inputs:
        - artifact: (optional) The code scaffold artifact from a prior step
        - code_text: (optional) Raw code scaffold text
        - architecture_text: (optional) Raw architecture text
        - requirements_text: (optional) Raw requirements text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The comprehensive project documentation
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract context from artifact or raw text
        context_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            context_text = inputs["artifact"].get("content", "")
        if not context_text:
            context_text = inputs.get("code_text", "")
        if not context_text:
            context_text = inputs.get("architecture_text", "")
        if not context_text:
            context_text = inputs.get("requirements_text", "")

        if not context_text:
            return {"status": "error", "message": "No code, architecture, or requirements provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a technical writer and documentation expert. Based on the following code structure,
architecture, and requirements, generate comprehensive project documentation including:

1. **README.md** — Project overview and quick start
   - Project description and purpose
   - Key features
   - Prerequisites and installation
   - Quick start guide
   - Contributing guidelines
   - License information

2. **API Documentation** — Endpoint and module documentation
   - API endpoint descriptions
   - Request/response formats
   - Authentication requirements
   - Error codes and handling
   - Code examples for each endpoint
   - Rate limiting and quotas

3. **Architecture Documentation** — System design overview
   - System architecture diagram (ASCII or Mermaid)
   - Component descriptions
   - Data flow diagrams
   - Technology stack details
   - Design patterns used
   - Scalability considerations

4. **Setup and Installation Guide** — Step-by-step setup
   - Development environment setup
   - Database setup and migrations
   - Configuration and environment variables
   - Dependency installation
   - Running locally
   - Running tests

5. **Deployment Documentation** — Production deployment guide
   - Deployment architecture
   - Pre-deployment checklist
   - Step-by-step deployment process
   - Docker/container deployment
   - Cloud platform setup (AWS, GCP, Azure)
   - Monitoring and logging setup
   - Rollback procedures
   - Scaling strategies

6. **User Guide** — How to use the system
   - Feature overview
   - Step-by-step tutorials
   - Common workflows
   - Troubleshooting guide
   - FAQ section
   - Screenshots or diagrams where applicable

7. **Developer Guide** — For contributors
   - Code organization and structure
   - Development workflow
   - Coding standards and conventions
   - Testing guidelines
   - Git workflow and branching strategy
   - Release process
   - Documentation standards

8. **CHANGELOG** — Version history
   - Version releases with dates
   - New features added
   - Bug fixes
   - Breaking changes
   - Migration guides for breaking changes
   - Deprecated features

9. **Database Schema Documentation** — Data model reference
   - Entity-relationship diagrams
   - Table descriptions
   - Column definitions and types
   - Relationships and foreign keys
   - Indexes and performance notes
   - Example queries

10. **Operations Guide** — Running in production
    - Monitoring and alerting setup
    - Backup and recovery procedures
    - Performance tuning
    - Security hardening
    - Incident response procedures
    - Health checks and readiness

For each document section, provide:
- File path and name
- Complete markdown content
- Code examples where applicable
- ASCII diagrams where helpful
- Links between related documentation

Code, Architecture & Requirements:
{context_text}

Generate comprehensive project documentation:"""

        result = provider.generate(prompt)
        documentation = result.get("response", "")

        return {
            "artifact": {
                "type": "documentation",
                "content": documentation,
            },
            "artifact_name": "documentation_v1",
            "status": "success",
        }
