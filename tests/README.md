# tests/

This directory contains all automated tests for the Slugger system.

## Purpose

Tests verify that the system behaves correctly, prevent regressions, and document expected behavior. Testing is a required part of every feature, not an optional afterthought.

## Structure

| Path | Contents |
|------|----------|
| `unit/` | Unit tests for individual components |
| `integration/` | Integration tests across multiple components |
| `validation/` | Artifact and output validation tests |
| `fixtures/` | Shared test fixtures and mock data |
| `conftest.py` | pytest configuration and shared fixtures |

## Conventions

- Tests are written using `pytest`.
- Test file names mirror the module they test (e.g., `test_orchestrator.py`).
- Tests describe observable behavior, not implementation details.
- Use `fixtures/` for shared test data rather than duplicating it.
- Use mock providers (`providers/mock_provider.py`) to avoid live AI calls in tests.
- Minimum test coverage thresholds are enforced in CI.

## Running Tests

```bash
pytest tests/
```

## Related

- `core/` — core interfaces tested in isolation via unit tests
- `agents/` — agent behavior verified in unit and integration tests
- `providers/` — mock provider used in tests to avoid AI costs
