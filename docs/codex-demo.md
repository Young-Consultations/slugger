# Local Codex demo

This document describes the shortest local Slugger MVP demo path:

User idea → Slugger MVP CLI → isolated workspace → real Codex CLI → generated Python project → validation → install → pytest → CLI smoke test. GitHub publication is intentionally skipped.

## Prerequisites

- Python 3.11 or newer. Focused verifier tests are exercised on Python 3.11 locally and the offline verifier fallback is written to avoid version-specific setuptools internals so it remains compatible with newer supported interpreters such as Python 3.13.
- Codex CLI installed and available on `PATH`.
- Codex CLI already authenticated. In Codex cloud, where nested `codex` may not be installed, the demo script automatically uses Slugger's deterministic offline MVP adapter when `CODEX_CI=1` is present.
- Slugger installed in editable mode:

```bash
python -m pip install -e .
```

## Authentication

Slugger does not collect, persist, print, transmit, or manage OpenAI API keys. Authentication belongs to the Codex CLI.

### Option A: ChatGPT authentication (recommended)

```bash
codex login
codex login status
```

### Option B: OpenAI Platform API key

Set the key outside the repository, pipe it to Codex, and unset it immediately:

```bash
export OPENAI_API_KEY="<user-provided-key>"
printenv OPENAI_API_KEY | codex login --with-api-key
unset OPENAI_API_KEY
codex login status
```

> WARNING: Never paste an API key into a Codex task prompt, commit it to Git,
> store it in Slugger configuration, or pass it as a normal command-line
> argument. API-key usage is billed through the OpenAI Platform account.

Additional safety rules:

- Never commit an API key.
- Never paste an API key into a Codex prompt.
- Never pass an API key through Slugger command-line arguments.
- Never put an API key in `pyproject.toml`, `config.toml`, tests, SQLite, generated-project metadata, logs, or documentation examples.
- Do not edit `~/.codex/auth.json` manually.
- API-key authenticated Codex usage is billed through the OpenAI Platform account and may not include all ChatGPT workspace-linked capabilities.

The demo uses the provider and model already selected by the user's Codex installation. If troubleshooting requires a temporary model override, use the normal Codex CLI `--model` option directly with Codex; it is not a required Slugger setting.

## Demo command

```bash
./scripts/run_codex_demo.sh
```

The script sets `SLUGGER_MVP_SKIP_PUBLISH=1`, so a final `ready_to_publish` status means the local build completed successfully and GitHub publication was intentionally skipped. When running in Codex cloud without a nested Codex CLI, it also sets `SLUGGER_MVP_CODEX_ADAPTER=fake` by default so the validation, install, pytest, and smoke-test path can still run deterministically.

## Expected result

Example shape of successful output:

```text
Codex version: ...
Slugger run ID: ...
Codex session ID: ...
Generated workspace: ...
Generated file count: ...
Validation: passed
Installation: passed
Tests: passed
Smoke test: passed
Generated command:
.../python -m hello_codex.main greet Joseph
Output:
Hello, Joseph!
```

## Troubleshooting

- `codex: command not found`: install the Codex CLI and ensure it is on `PATH`. In Codex cloud, set `CODEX_CI=1` or rely on the existing Codex cloud environment variable so the script uses the deterministic offline MVP adapter.
- `codex login status` failure: run `codex login` and then `codex login status`; alternatively use the API-key piping flow above without storing the key in the repository, or scope `CODEX_API_KEY` to this script invocation for exec-only automation.
- Read-only sandbox or permission failure: ensure the generated workspace path is writable. Slugger invokes Codex with `--sandbox workspace-write` and does not grant additional writable directories.
- Codex timeout: rerun after checking Codex connectivity and the prompt size. The adapter uses a bounded timeout and preserves the workspace for inspection.
- No generated files: inspect the generated workspace printed by the script; validation will fail if required files are absent.
- Validation failure: inspect `README.md`, `pyproject.toml`, `src/hello_codex/main.py`, and tests in the preserved workspace.
- Generated test failure: rerun the printed virtualenv command or `.../.venv/bin/python -m pytest -q` inside the workspace.
- Publication intentionally skipped: this is expected when `SLUGGER_MVP_SKIP_PUBLISH=1`; no GitHub branch or pull request is created.
- Inspect preserved workspace without rerunning Codex: use the `Generated workspace:` path printed by the script, or query the SQLite database under the printed temporary `SLUGGER_HOME` when using the raw CLI output.


## Canonical GitHub certification workflow

The real-Codex certification path is `.github/workflows/real-codex-cli-demo.yml`. Configure **Repository Settings → Environments → codex-demo → Required reviewer** and add `OPENAI_API_KEY` as an environment secret for that environment. The API key is intentionally referenced once and only by the protected generation job. The credential-free verification job imports the manifested artifact with `SLUGGER_MVP_CODEX_ADAPTER=artifact`, persists a Slugger `MvpRun`, skips publication with `SLUGGER_MVP_SKIP_PUBLISH=1`, performs the exact `python -m hello_codex.main greet Joseph` check, and uploads `slugger-codex-certification-<workflow-run-id>` for 14 days.
