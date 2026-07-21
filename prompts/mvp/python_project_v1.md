# Slugger MVP Python project prompt v1

Generate an intentionally small, deterministic Python 3.11 or newer project for the user's idea inside the current working directory only.

Requirements:
- Use a `src/` layout with package source under `src/<package_name>/`.
- Create these files: `README.md`, `pyproject.toml`, `src/<package_name>/__init__.py`, `src/<package_name>/main.py`, and `tests/test_main.py`.
- Include `pyproject.toml` with a conventional supported build backend such as `setuptools.build_meta`.
- Keep runtime dependencies empty unless strictly necessary for the user's requested demo behavior.
- Include at least three pytest tests that run without network access.
- Include one pytest test that proves `python -m {package_name}.main greet Joseph` emits exactly `Hello, Joseph!`.
- Declare pytest as an installable test dependency, preferably with `[project.optional-dependencies]` and `test = ["pytest>=8,<10"]`, so `pip install .[test]` makes `python -m pytest` available in a fresh virtual environment.
- Include a package entry point that can be executed with `python -m <package_name>.main`.
- The generated README must include fresh-checkout instructions in this order: `python -m venv .venv`, `. .venv/bin/activate`, a Windows activation equivalent such as `.venv\\Scripts\\activate`, `python -m pip install --upgrade pip`, `python -m pip install -e '.[test]'`, `python -m pytest -q`, and `python -m <package_name>.main --help`. Installation must appear before module execution.
- Use `argparse` for the demo CLI.
- Ensure `python -m <package_name>.main --help` exits with status zero.
- Display conventional usage output for `--help`.
- Include the project name in the help output.
- Implement a `greet NAME` command using argparse that prints exactly `Hello, NAME!` followed by one newline.
- Keep conventional `--help` behavior.
- Use no runtime dependencies.
- Do not use external services, network calls, Git operations, or files outside the assigned output directory.
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
