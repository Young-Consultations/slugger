"""Create deterministic sanitized certification records from workflow evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--output-root", type=Path, default=Path("docs/certification/runs")
    )
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    out = args.output_root / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    sanitized = {
        key: evidence.get(key)
        for key in sorted(evidence)
        if key.lower()
        not in {"env", "environment", "authorization", "token", "secret", "api_key"}
    }
    (out / "verification-evidence.json").write_text(
        json.dumps(sanitized, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "generated-project-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = [
        f"# Certification summary: run {args.run_id}",
        "",
        f"- Workflow run ID: {args.run_id}",
    ]
    if evidence.get("workflow_name"):
        summary.append(f"- Workflow: {evidence['workflow_name']}")
    if evidence.get("final_status"):
        summary.append(f"- Final status: {evidence['final_status']}")
    (out / "certification-summary.md").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
