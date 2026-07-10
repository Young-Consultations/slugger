# services/

External service abstractions and adapters used by Slugger.

Each sub-package follows the same hexagonal-architecture pattern:

| Package | Interface | Concrete client | Mock | Purpose |
|---------|-----------|-----------------|------|---------|
| `services/github/` | `IGitHubService` | `GitHubClient` | `MockGitHubService` | GitHub REST API (issues, PRs, comments) |
| `services/canva/` | `ICanvaService` | `CanvaClient` | `MockCanvaService` | Canva Connect API (designs, exports, brand templates) |

## Adding a new service

1. Create a sub-package under `services/<name>/`.
2. Define domain models in `models.py`.
3. Define the abstract interface in `base.py`.
4. Implement the concrete client in `client.py`.
5. Provide a `MockService` in `mock_service.py` for offline/test use.
6. Export all public symbols from `__init__.py`.
7. Update `services/__init__.py` to re-export the new symbols.
8. Add configuration to `config/defaults.yaml`, `config/secrets.yaml.example`, `config/settings.py`, and `config/loader.py`.
9. Write tests in `tests/test_<name>_service.py`.
