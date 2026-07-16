"""Minimal restricted-container entry point for generated MVP verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from mvp.verification_service import ExistingProjectVerifier


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mvp.verify_cli",
        description="Verify a generated MVP project without importing Slugger bootstrap code.",
    )
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--evidence-file", required=True, type=Path)
    parser.add_argument(
        "--no-container",
        action="store_true",
        help="Accepted for compatibility; this minimal entry point never starts Docker.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = ExistingProjectVerifier(
        args.workspace_root,
        use_container=False,
        evidence_file=args.evidence_file,
    ).verify_existing(project_dir=args.project_dir, project_name=args.project_name)
    summary = {
        "status": result.status.value,
        "project_name": result.project_name,
        "failure_phase": result.failure_phase.value if result.failure_phase else None,
        "failure_message": result.failure_message,
        "generated_source_changed": result.generated_source_changed,
        "evidence_file": str(result.evidence_file),
    }
    print(json.dumps(summary, sort_keys=True)[:4000])
    return 0 if result.status.value == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
