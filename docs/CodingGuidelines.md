<!--
  docs/CodingGuidelines.md
  Purpose: language-agnostic coding guidelines; include language-specific rules in subfolders.
-->

# Coding Guidelines

## Goal
Write readable, maintainable, and testable code. Favor clarity over cleverness.

## Style & conventions
- Follow the language-specific style guide (e.g., gofmt for Go, Black/PEP8 for Python, Prettier/ESLint for JS/TS).
- Prefer descriptive names for functions, types, and variables.
- Keep functions small and single-responsibility.

## Error handling
- Handle errors explicitly and return context-rich errors.
- Avoid swallowing errors; propagate or log with context.

## Logging
- Use structured logging (JSON) where possible.
- Log at appropriate levels and avoid logging sensitive data.

## Testing
- Cover happy-path and edge cases in unit tests.
- Use mocks for external dependencies; use integration tests for end-to-end validation.
- Keep test data small and focused.

## APIs
- Design versioned, backward-compatible APIs.
- Use consistent response shapes and meaningful HTTP status codes.

## Security & input validation
- Validate all external inputs and enforce sensible size limits.
- Use parameterized queries for any database interactions.
- Avoid exposing implementation details in error responses.

## Performance
- Measure before optimizing; prefer clear code until profiling indicates hotspots.
- Document any non-obvious performance tradeoffs.

## Comments & documentation
- Prefer self-documenting code. Use comments to explain "why", not "what".
- Keep public APIs documented and maintain examples where helpful.

## Linters & tooling
- Configure linters and static analysis in CI.
- Add pre-commit hooks for formatting.

## Example (pseudo-code)
<!--
  // Good: Small, explicit function with clear error semantics
  func GenerateSlug(ctx context.Context, input string) (string, error) { ... }
-->

## Language-specific notes
- Add language-specific guideline files (e.g., `docs/python.md`, `docs/go.md`) when the repo contains multiple languages.

