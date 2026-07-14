# Slugger MVP Python project prompt v1

Generate an intentionally small, deterministic Python 3.11 or newer project for the user's idea inside the current working directory only.

Requirements:
- Use a `src/` layout with package source under `src/<package_name>/`.
- Create these files: `README.md`, `pyproject.toml`, `src/<package_name>/__init__.py`, `src/<package_name>/main.py`, and `tests/test_main.py`.
- Include `pyproject.toml` with a conventional supported build backend such as `setuptools.build_meta`.
- Keep runtime dependencies empty unless strictly necessary for the user's requested demo behavior.
- Include pytest tests that run without network access.
- Include a package entry point that can be executed with `python -m <package_name>.main`.
- Use `argparse` for the demo CLI.
- Ensure `python -m <package_name>.main --help` exits with status zero.
- Display conventional usage output for `--help`.
- Include the project name in the help output.
- For command-line ideas, implement only the smallest deterministic behavior necessary to satisfy the request.
- Finish by ensuring the generated tests pass.

Safety and scope constraints:
- Do not create credential files, `.env` files, private keys, runtime databases, unsupported binary assets, deployment infrastructure, or generated files outside the workspace.
- Do not use external services.
- Do not use databases.
- Do not use GUI frameworks.
- Do not use web frameworks.
- Do not create background processes.
- Do not use Docker.
- Do not use the network.
- Do not create a nested Git repository.
- Do not run Git commands.
- Do not commit, push, publish, deploy, or open pull requests.
- Do not modify anything outside the current working directory.
- Do not modify Slugger itself.

Project metadata:
- Project name: `{project_name}`
- Python package name: `{package_name}`
- Template: `{template}`
- Idea: `{idea}`

After generating files and ensuring tests pass, stop.
