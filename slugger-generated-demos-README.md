# Slugger Generated Demos

This README is intended for the root of `Young-Consultations/slugger-generated-demos`.

`slugger-generated-demos` is a Slugger-managed sandbox repository related to `Young-Consultations/slugger`. Slugger publishes generated Python CLI demos here as draft pull requests so maintainers can inspect the output before any merge.

Generated code requires human review. Generated examples are not automatically production-ready, and generated security or cryptography examples are educational unless independently reviewed by qualified maintainers.

Maintainers should not manually edit Slugger-owned branches (`slugger/generated-*`) unless recovering from a failed run. Do not automatically merge generated application pull requests.

## Review a generated Python project

From a fresh checkout of a generated PR branch:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
python -m pytest -q
python -m <package_name>.main --help
```

On Windows, activate the environment with `.venv\\Scripts\\activate` before running the pip, pytest, and CLI commands.

Review the draft PR body, generated file inventory, tests, and CLI behavior before deciding whether to close, revise, or merge the generated output.
