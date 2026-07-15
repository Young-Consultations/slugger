You are generating a Slugger MVP Python CLI demo for a GitHub Actions workflow.

Create the complete project only under `generated-demo/`. Do not modify any file outside `generated-demo/`.

Inspect the repository's MVP contract (`mvp/project_validator.py`, `mvp/basic_runner.py`, `prompts/mvp/python_project_v1.md`) and follow that contract rather than inventing another layout.

Requirements:
- Project name must be `codex-cli-demo` unless existing workflow context explicitly provides another lowercase kebab-case name.
- Use Python >=3.11 and a standard `src/` layout.
- Include `pyproject.toml`, `README.md`, `src/<package>/__init__.py`, `src/<package>/main.py`, and pytest tests under `tests/`.
- Support `python -m <package>.main --help` and at least one useful command beyond help.
- Runtime dependencies must be empty. Test dependency may be pinned/bounded pytest only.
- Use `setuptools.build_meta`; do not use custom or in-tree build backends.
- Do not create `.git`, `.github`, workflow, deployment, hook, infrastructure, network, GUI, web, database, daemon, background-process, symlink, binary, secret, token, credential, direct URL dependency, Git dependency, local path dependency, or package-index configuration files.
- Do not initialize a nested Git repository.

When done, summarize only the files created and do not run, install, import, or test the generated project.
