You are generating a Slugger MVP Python CLI demo for a GitHub Actions workflow.

Create the complete project only under `{output_dir}/`. Do not modify any file outside `{output_dir}/`.

Exact generation inputs:
- Project name: `{project_name}`
- Python package name: `{package_name}`
- Output directory: `{output_dir}`
- CLI/README description: `{demo_description}`

Inspect the repository's MVP contract (`mvp/project_validator.py`, `mvp/basic_runner.py`, `prompts/mvp/python_project_v1.md`) and follow that contract rather than inventing another layout.

Requirements:
- Use the exact project name `{project_name}` in `pyproject.toml` and CLI help.
- Use the exact Python package directory `src/{package_name}/`.
- The selected description must appear in README.md or the argparse CLI description.
- Use Python >=3.11 and a standard `src/` layout.
- Include `pyproject.toml`, `README.md`, `src/{package_name}/__init__.py`, `src/{package_name}/main.py`, and pytest tests under `tests/`.
- Support `python -m {package_name}.main --help` and at least one useful command beyond help.
- Include at least three generated pytest tests.
- Runtime dependencies must be exactly empty: `[project] dependencies = []`.
- Test dependency must be exactly `[project.optional-dependencies] test = ["pytest>=8,<10"]`.
- Use `setuptools.build_meta`; do not use custom or in-tree build backends.
- Do not create `.git`, `.github`, workflow, deployment, hook, infrastructure, network, GUI, web, database, daemon, background-process, symlink, binary, secret, token, credential, direct URL dependency, Git dependency, local path dependency, editable external dependency, dependency link, arbitrary pytest plugin, or package-index configuration files.
- Do not initialize a nested Git repository.

When done, summarize only the files created and do not run, install, import, or test the generated project.
