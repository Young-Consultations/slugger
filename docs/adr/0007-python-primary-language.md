# ADR 0007: Python as Primary Language

Status: Accepted

## Context

Slugger is an AI Software Factory that orchestrates specialized agents, manages workflows, integrates with AI providers, and generates engineering artifacts. The choice of primary implementation language has far-reaching consequences for developer productivity, library availability, AI/ML ecosystem compatibility, and long-term maintainability.

Key considerations:
- Most AI and ML libraries are Python-first (OpenAI SDK, Anthropic SDK, LangChain, etc.)
- The AI engineering community has strong Python expertise
- Python's dynamic typing and scripting capabilities accelerate prompt experimentation
- Slugger needs rapid iteration cycles compatible with AI development workflows

## Decision

Adopt **Python** as the primary implementation language for Slugger.

Specific standards:
- Target Python 3.11 or later to benefit from improved type hints, `tomllib`, and performance improvements.
- Enforce PEP 8 style and enforce it through automated tooling (e.g., `ruff` or `flake8`).
- Require type hints on all public interfaces.
- Use `pyproject.toml` for project metadata and dependency management.
- Prefer `pip` with a `requirements.txt` or `pyproject.toml` for dependency management.

## Consequences

**Positive:**
- Native compatibility with OpenAI, Anthropic, and other AI provider SDKs.
- Rich ecosystem for data processing, template rendering, YAML/JSON handling, and CLI tooling.
- Large pool of contributors familiar with Python in the AI/ML domain.
- Rapid prototyping and iteration capabilities.
- Strong tooling for testing (`pytest`), documentation (`mkdocs`, `sphinx`), and linting.

**Negative:**
- Python is generally slower than compiled languages; performance-critical sections may require profiling.
- Global Interpreter Lock (GIL) limits true parallelism; async (`asyncio`) patterns are required for concurrent agent execution.
- Dynamic typing increases the importance of thorough type hinting and runtime validation.
