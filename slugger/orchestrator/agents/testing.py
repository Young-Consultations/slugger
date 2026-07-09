"""Testing agent.

This agent accepts code scaffolds and architecture design, and generates
unit test templates, integration test scaffolds, test fixtures, and mocks.
"""
from typing import Any, Dict

from slugger.orchestrator.agents.base import Agent


class TestingAgent(Agent):
    name = "testing"

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test scaffolds and fixtures from code and architecture.

        Expects inputs:
        - artifact: (optional) The code scaffold artifact from a prior step
        - code_text: (optional) Raw code scaffold text
        - architecture_text: (optional) Raw architecture text
        - _provider: (injected by Orchestrator) The AI provider

        Returns:
        - artifact: The test scaffolds, fixtures, and mocks
        - artifact_name: A name for the artifact
        - status: 'success' or 'error'
        """
        provider = inputs.get("_provider")

        # Extract code or architecture from artifact or raw text
        context_text = ""
        if "artifact" in inputs and isinstance(inputs["artifact"], dict):
            context_text = inputs["artifact"].get("content", "")
        if not context_text:
            context_text = inputs.get("code_text", "")
        if not context_text:
            context_text = inputs.get("architecture_text", "")

        if not context_text:
            return {"status": "error", "message": "No code or architecture provided"}
        if not provider:
            return {"status": "error", "message": "No provider available"}

        prompt = f"""You are a QA engineer and testing expert. Based on the following code structure and architecture,
generate comprehensive test scaffolds including:

1. **Unit Tests** — Test individual functions and classes
   - Test file structure (tests/unit/test_*.py or similar)
   - Test class templates with setup/teardown
   - Test method templates for each function/method
   - Test data fixtures

2. **Integration Tests** — Test component interactions
   - Integration test structure (tests/integration/test_*.py)
   - Setup and teardown for integration environment
   - Mocked external dependencies
   - End-to-end workflow tests

3. **Test Fixtures** — Reusable test data and setup
   - Fixture factory functions
   - Mock data generators
   - Database seeding scripts
   - Configuration for test environments

4. **Mocks and Stubs** — Isolate code under test
   - Mock classes for external services
   - Stub implementations for dependencies
   - Mock factory patterns
   - Response templates for API mocks

5. **Test Coverage Configuration** — Measure and enforce coverage
   - Coverage configuration file (.coveragerc, pytest.ini)
   - Coverage targets and thresholds
   - Exclusion patterns

6. **CI/CD Testing Pipeline** — Automate test execution
   - GitHub Actions workflow for tests
   - Pre-commit hooks for test execution
   - Test result reporting
   - Coverage badge generation

7. **Performance and Load Tests** — Verify scalability
   - Load test scenarios
   - Performance benchmarks
   - Resource utilization tests

8. **Security Tests** — Verify security controls
   - Input validation tests
   - Authentication/authorization tests
   - SQL injection and XSS prevention tests
   - API security tests

For each test, provide:
- File path and name
- Test skeleton (imports, class structure, test methods)
- Test data and fixtures
- Expected behaviors and assertions
- Implementation notes and TODOs

Code Structure & Architecture:
{context_text}

Generate comprehensive test scaffolds:"""

        result = provider.generate(prompt)
        test_scaffold = result.get("response", "")

        return {
            "artifact": {
                "type": "test_scaffold",
                "content": test_scaffold,
            },
            "artifact_name": "test_scaffold_v1",
            "status": "success",
        }
