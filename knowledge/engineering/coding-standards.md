# Python Coding Standards

- Follow PEP 8 and prefer explicit, descriptive naming.
- Use type hints for public functions, methods, and dataclass fields.
- Prefer dataclasses for core models to keep dependencies minimal.
- Keep modules focused; split files before they become difficult to navigate.
- Prefer composition, dependency injection, and pure functions where practical.
- Use docstrings on public classes and methods.
- Avoid hardcoded secrets, endpoints, or environment-specific paths.
- Keep side effects at the edges of the system behind interfaces.
- Write unit tests for core behavior and regression-prone logic.
