"""Command line interface for Slugger."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import cast

from models.project import CodingAgent, Platform, ProjectInput
from orchestrator import Bootstrap, Slugger
from mvp.runtime_paths import diagnostics as runtime_diagnostics

_PLATFORMS = [p.value for p in Platform]
_CODING_AGENTS = [a.value for a in CodingAgent]


def _approval_store(root_path: Path):
    from workflow.durable_approvals import DurableApprovalStore

    return DurableApprovalStore(root_path / "workflow" / "approvals.db")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slugger", description="Slugger AI Software Factory CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build — single-input entry point
    build_parser = subparsers.add_parser(
        "build", help="Build an app from a single structured input"
    )
    build_parser.add_argument("idea", help="Description of the app idea to build")
    build_parser.add_argument(
        "--platform",
        choices=_PLATFORMS,
        required=True,
        metavar="PLATFORM",
        help=f"Target output platform: {', '.join(_PLATFORMS)}",
    )
    build_parser.add_argument(
        "--coding-agent",
        choices=_CODING_AGENTS,
        default=CodingAgent.CODEX.value,
        dest="coding_agent",
        metavar="AGENT",
        help=f"Coding agent to use: {', '.join(_CODING_AGENTS)} (default: {CodingAgent.CODEX.value})",
    )
    build_parser.add_argument(
        "--workflow",
        default=None,
        help="Override the default workflow (name or YAML path)",
    )

    # resume — continue a previously interrupted build
    resume_parser = subparsers.add_parser(
        "resume", help="Resume a previously interrupted build"
    )
    resume_parser.add_argument(
        "run_id", help="Run ID returned by the original build command"
    )
    resume_parser.add_argument(
        "--idea", default=None, help="Original idea (forwarded as metadata)"
    )
    resume_parser.add_argument(
        "--platform",
        choices=_PLATFORMS,
        default=None,
        metavar="PLATFORM",
        help="Original platform (forwarded as metadata)",
    )
    resume_parser.add_argument(
        "--coding-agent",
        choices=_CODING_AGENTS,
        default=None,
        dest="coding_agent",
        metavar="AGENT",
        help="Original coding agent (forwarded as metadata)",
    )

    run_parser = subparsers.add_parser("run", help="Run a workflow recipe")
    run_parser.add_argument("workflow", help="Workflow name or YAML path")
    list_parser = subparsers.add_parser("list", help="List runtime assets")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)
    list_subparsers.add_parser("agents", help="List available agents")
    list_subparsers.add_parser("workflows", help="List available workflows")
    subparsers.add_parser("status", help="Show system status")

    mvp_parser = subparsers.add_parser("mvp", help="Run focused MVP commands")
    mvp_subparsers = mvp_parser.add_subparsers(dest="mvp_command", required=True)
    mvp_build = mvp_subparsers.add_parser(
        "build", help="Build a Python project through the MVP path"
    )
    mvp_build.add_argument("idea", help="Description of the Python project to generate")
    mvp_build.add_argument(
        "--name",
        required=True,
        dest="project_name",
        help="Lowercase kebab-case project name",
    )
    mvp_build.add_argument(
        "--template", default="cli", choices=["cli"], help="MVP project template"
    )
    mvp_build.add_argument(
        "--repo",
        required=True,
        dest="github_repository",
        help="GitHub repository in owner/repository form",
    )
    mvp_build.add_argument(
        "--base",
        default="main",
        dest="base_branch",
        help="Base branch for the draft pull request",
    )

    # lineage — show artifact traceability (WP-020)
    lineage_parser = subparsers.add_parser(
        "lineage", help="Show artifact lineage and traceability"
    )
    lineage_parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        dest="lineage_format",
        help="Output format: json or summary (default: summary)",
    )

    # approvals — manage approval gates (WP-024)
    approvals_parser = subparsers.add_parser(
        "approvals", help="Manage workflow approval gates"
    )
    approvals_subparsers = approvals_parser.add_subparsers(
        dest="approvals_command", required=True
    )
    approvals_subparsers.add_parser("list", help="List pending approval records")
    approvals_show = approvals_subparsers.add_parser(
        "show", help="Show approval request details"
    )
    approvals_show.add_argument("request_id", help="Approval request ID")
    approvals_approve = approvals_subparsers.add_parser(
        "approve", help="Approve a pending request"
    )
    approvals_approve.add_argument("request_id", help="Approval request ID")
    approvals_approve.add_argument(
        "--rationale", required=True, help="Approval rationale"
    )
    approvals_reject = approvals_subparsers.add_parser(
        "reject", help="Reject a pending request"
    )
    approvals_reject.add_argument("request_id", help="Approval request ID")
    approvals_reject.add_argument(
        "--rationale", required=True, help="Rejection rationale"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root_path = Path(__file__).resolve().parent.parent
    slugger: Slugger | None = None

    def get_slugger() -> Slugger:
        nonlocal slugger
        if slugger is None:
            slugger = Slugger(Bootstrap(root_path).build())
        return slugger

    if args.command == "mvp" and args.mvp_command == "build":
        from mvp.build_service import production_mvp_build_service
        from mvp.models import MvpProjectRequest

        request = MvpProjectRequest(
            idea=args.idea,
            project_name=args.project_name,
            template=args.template,
            github_repository=args.github_repository,
            base_branch=args.base_branch,
        )
        mvp_result = production_mvp_build_service(root_path).build(request)
        run = mvp_result.run
        runtime = runtime_diagnostics()
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "status": run.status.value,
                    "workspace_path": run.workspace_path,
                    "runtime": runtime,
                    "workspace_root": runtime["workspace_root"],
                    "sqlite_path": runtime["sqlite_path"],
                    "generated_files": len(run.inventory.files) if run.inventory else 0,
                    "validation_passed": bool(run.validation_results)
                    and all(check.passed for check in run.validation_results),
                    "test_passed": bool(run.test_results)
                    and all(check.passed for check in run.test_results),
                    "smoke_passed": any(
                        check.name == "cli_smoke" and check.passed
                        for check in run.test_results
                    ),
                    "github_branch": run.github_publish_result.branch
                    if run.github_publish_result
                    else None,
                    "codex_session_id": run.codex_session_id,
                    "slugger_correlation_id": run.slugger_correlation_id,
                    "prompt_version": run.prompt_version,
                    "prompt_hash": run.prompt_hash,
                    "source_integrity_result": run.source_integrity_result,
                    "source_hash_before_codex": run.source_hash_before_codex,
                    "source_hash_after_codex": run.source_hash_after_codex,
                    "changed_source_paths": list(run.changed_source_paths),
                    "publication_skipped": run.publication_skipped,
                    "draft_pr_url": run.github_publish_result.pull_request_url
                    if run.github_publish_result
                    else None,
                    "error_details": run.error_details,
                }
            )
        )
        return 0 if run.status.value in {"completed", "ready_to_publish"} else 1
    if args.command == "build":
        slugger = get_slugger()
        project_input = ProjectInput(
            idea=args.idea,
            platform=Platform(args.platform),
            coding_agent=CodingAgent(args.coding_agent),
        )
        result = slugger.build(project_input, workflow=args.workflow)
        outcome = result.outcome.value if result.outcome is not None else "unknown"
        print(
            json.dumps(
                {
                    "run_id": result.run_id,
                    "idea": project_input.idea,
                    "platform": project_input.platform.value,
                    "coding_agent": project_input.coding_agent.value,
                    "workflow": result.definition.name,
                    "status": result.status,
                    "outcome": outcome,
                    "artifacts": len(result.artifacts),
                }
            )
        )
        return 0
    if args.command == "resume":
        slugger = get_slugger()
        resume_input: ProjectInput | None = None
        if args.idea and args.platform:
            resume_input = ProjectInput(
                idea=args.idea,
                platform=Platform(args.platform),
                coding_agent=CodingAgent(args.coding_agent)
                if args.coding_agent
                else CodingAgent.CODEX,
            )
        result = slugger.resume(args.run_id, project_input=resume_input)
        outcome = result.outcome.value if result.outcome is not None else "unknown"
        print(
            json.dumps(
                {
                    "run_id": result.run_id,
                    "workflow": result.definition.name,
                    "status": result.status,
                    "outcome": outcome,
                    "artifacts": len(result.artifacts),
                }
            )
        )
        return 0
    if args.command == "run":
        slugger = get_slugger()
        result = slugger.run_workflow(args.workflow)
        outcome = result.outcome.value if result.outcome is not None else "unknown"
        print(
            json.dumps(
                {
                    "workflow": result.definition.name,
                    "status": result.status,
                    "outcome": outcome,
                    "artifacts": len(result.artifacts),
                }
            )
        )
        return 0
    if args.command == "list" and args.list_command == "agents":
        slugger = get_slugger()
        print("\n".join(slugger.list_agents()))
        return 0
    if args.command == "list" and args.list_command == "workflows":
        slugger = get_slugger()
        print("\n".join(slugger.list_workflows()))
        return 0
    if args.command == "status":
        slugger = get_slugger()
        print(json.dumps(slugger.status(), indent=2))
        return 0
    if args.command == "lineage":
        slugger = get_slugger()
        lineage_data = slugger.lineage()
        if args.lineage_format == "json":
            print(json.dumps(lineage_data, indent=2))
        else:
            nodes = cast(list[dict[str, object]], lineage_data.get("nodes") or [])
            if not nodes:
                print("No lineage data available.")
            else:
                print(f"Artifact lineage: {len(nodes)} node(s)")
                for node in nodes:
                    parents = (
                        ", ".join(cast(list[str], node.get("parent_ids") or []))
                        or "none"
                    )
                    print(
                        f"  [{node.get('stage', '?')}] {node.get('name', '?')} "
                        f"(id={node.get('artifact_id', '?')}, parents={parents})"
                    )
        return 0
    if args.command == "approvals":
        store = _approval_store(root_path)
        actor = os.environ.get("USER", "cli")
        if args.approvals_command == "list":
            print(json.dumps(store.list_requests(), indent=2))
            return 0
        if args.approvals_command == "show":
            print(json.dumps(store.get_request(args.request_id), indent=2))
            return 0
        if args.approvals_command == "approve":
            print(
                json.dumps(
                    store.record_decision(
                        args.request_id, actor, "approve", args.rationale
                    ),
                    indent=2,
                )
            )
            return 0
        if args.approvals_command == "reject":
            print(
                json.dumps(
                    store.record_decision(
                        args.request_id, actor, "reject", args.rationale
                    ),
                    indent=2,
                )
            )
            return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
