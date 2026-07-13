# Slugger MVP Python project prompt v1

Generate a small Python 3.11 or newer project for the user's idea inside the current working directory.

Requirements:
- Use a `src/` layout.
- Keep runtime dependencies minimal.
- Include at least one meaningful pytest test.
- Create these files: `README.md`, `pyproject.toml`, `src/<package_name>/__init__.py`, `src/<package_name>/main.py`, and `tests/test_main.py`.
- Do not create credential files, `.env` files, private keys, runtime databases, unsupported binary assets, deployment infrastructure, or generated files outside the workspace.
- Do not run Git commands.
- Do not modify anything outside the current working directory.

Project metadata:
- Project name: `{project_name}`
- Python package name: `{package_name}`
- Template: `{template}`
- Idea: `{idea}`

After generating files, stop. Do not commit, push, publish, deploy, or open pull requests.
