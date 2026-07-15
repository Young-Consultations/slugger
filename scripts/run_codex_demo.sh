#!/usr/bin/env bash
set -euo pipefail

if command -v codex >/dev/null 2>&1; then
  CODEX_VERSION="$(codex --version)"
  echo "Codex version: ${CODEX_VERSION}"
  if [[ -n "${CODEX_API_KEY:-}" ]]; then
    echo "Using scoped CODEX_API_KEY for codex exec; skipping codex login status."
  elif ! codex login status >/dev/null; then
    echo "Codex CLI authentication is not available." >&2
    echo "Run:" >&2
    echo "    codex login" >&2
    echo "    codex login status" >&2
    echo "Alternatively, authenticate with an OpenAI Platform API key by piping OPENAI_API_KEY to:" >&2
    echo "    codex login --with-api-key" >&2
    echo "Or scope CODEX_API_KEY to this script invocation for exec-only automation." >&2
    echo "Do not store the API key in this repository." >&2
    exit 1
  fi
elif [[ "${CODEX_CI:-}" == "1" ]]; then
  echo "Codex CLI is not available in this Codex cloud environment; using the deterministic offline MVP adapter." >&2
  export SLUGGER_MVP_CODEX_ADAPTER="${SLUGGER_MVP_CODEX_ADAPTER:-fake}"
else
  echo "codex: command not found" >&2
  echo "Install Codex CLI, then run: codex login && codex login status" >&2
  echo "In Codex cloud, rerun with CODEX_CI=1 to use the deterministic offline MVP adapter." >&2
  exit 127
fi

export SLUGGER_HOME="$(mktemp -d -t slugger-codex-demo-XXXXXX)"
export SLUGGER_MVP_SKIP_PUBLISH=1

IDEA=$'Create a Python command-line application named hello-codex.\nRequirements:\n- Provide a `greet NAME` command.\n- The command prints exactly `Hello, NAME!`.\n- Provide conventional `--help` output.\n- Use argparse.\n- Use a src-based package layout.\n- Include pytest tests.\n- Use no runtime dependencies.\n- Do not use the network.'

RESULT_JSON="$(python -m cli.main mvp build "$IDEA" --name hello-codex --template cli --repo local/hello-codex-demo)"
echo "${RESULT_JSON}"

python - "$RESULT_JSON" <<'PY'
import json
import subprocess
import sys
from pathlib import Path

result = json.loads(sys.argv[1])
workspace = Path(result["workspace_path"])
python = workspace / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
command = [str(python), "-m", "hello_codex.main", "greet", "Joseph"]
print(f"Slugger run ID: {result['run_id']}")
print(f"Codex session ID: {result.get('codex_session_id') or 'not reported'}")
print(f"Generated workspace: {workspace}")
print(f"Generated file count: {result.get('generated_files')}")
print(f"Validation: {'passed' if result.get('validation_passed') else 'failed'}")
print(f"Installation: {'passed' if result.get('test_passed') else 'failed'}")
print(f"Tests: {'passed' if result.get('test_passed') else 'failed'}")
print(f"Smoke test: {'passed' if result.get('smoke_passed') else 'failed'}")
print(f"Publication skipped: {result.get('publication_skipped')}")
print("Generated command:")
print(" ".join(command))
if result.get("status") not in {"ready_to_publish", "completed"}:
    raise SystemExit(f"Slugger build failed: {result.get('error_details')}")
completed = subprocess.run(command, cwd=workspace, text=True, capture_output=True, check=False)
print("Output:")
print(completed.stdout.strip())
if completed.returncode != 0:
    print(completed.stderr, file=sys.stderr)
    raise SystemExit(completed.returncode)
if completed.stdout.strip() != "Hello, Joseph!":
    raise SystemExit("Functional demo output did not match exactly")
PY
