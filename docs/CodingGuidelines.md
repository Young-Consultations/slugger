<!--
  docs/CodingGuidelines.md
  Purpose: language-agnostic coding guidelines; Python-specific notes since the project targets Python.
-->

# Coding Guidelines

## Goals
Write clear, maintainable, and well-tested code. Prioritize readability, explicitness, and testability.

## General principles
- Small functions with single responsibility.
- Descriptive names for functions, variables, and classes.
- Prefer explicit code over clever/obscure constructs.

## Python-specific recommendations
- Formatting: use `black` for code formatting.
- Linting: use `flake8` and consider `mypy` for optional static typing checks.
- Typing: add type annotations for public APIs and core logic where feasible.
- Packaging: follow standard Python packaging practices (setup.cfg / pyproject.toml).

## Error handling
- Fail fast with clear, contextual error messages.
- Avoid broad exception catches; handle expected error types explicitly.

## Testing
- Unit tests: isolate external dependencies via mocks.
- Integration tests: test agent orchestration and template rendering end-to-end in a controlled environment.
- Use fixtures to manage shared test setup and teardown.

## Logging
- Use structured logging with appropriate log levels.
- Avoid logging sensitive data; use redaction or avoid capturing secrets.

## Security
- Validate all inputs from external sources.
- Do not commit secrets; use environment variables or secret managers for runtime secrets.

## Documentation
- Document public modules and functions with docstrings.
- Keep higher-level design docs in `/docs` and link to them from README.

