"""Command line interface for Slugger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from models.project import CodingAgent, Platform, ProjectInput
from orchestrator import Bootstrap, Slugger

_PLATFORMS = [p.value for p in Platform]
_CODING_AGENTS = [a.value for a in CodingAgent]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='slugger', description='Slugger AI Software Factory CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # build — single-input entry point
    build_parser = subparsers.add_parser('build', help='Build an app from a single structured input')
    build_parser.add_argument('idea', help='Description of the app idea to build')
    build_parser.add_argument(
        '--platform',
        choices=_PLATFORMS,
        required=True,
        metavar='PLATFORM',
        help=f'Target output platform: {", ".join(_PLATFORMS)}',
    )
    build_parser.add_argument(
        '--coding-agent',
        choices=_CODING_AGENTS,
        default=CodingAgent.CODEX.value,
        dest='coding_agent',
        metavar='AGENT',
        help=f'Coding agent to use: {", ".join(_CODING_AGENTS)} (default: {CodingAgent.CODEX.value})',
    )
    build_parser.add_argument('--workflow', default=None, help='Override the default workflow (name or YAML path)')

    # resume — continue a previously interrupted build
    resume_parser = subparsers.add_parser('resume', help='Resume a previously interrupted build')
    resume_parser.add_argument('run_id', help='Run ID returned by the original build command')
    resume_parser.add_argument('--idea', default=None, help='Original idea (forwarded as metadata)')
    resume_parser.add_argument(
        '--platform',
        choices=_PLATFORMS,
        default=None,
        metavar='PLATFORM',
        help='Original platform (forwarded as metadata)',
    )
    resume_parser.add_argument(
        '--coding-agent',
        choices=_CODING_AGENTS,
        default=None,
        dest='coding_agent',
        metavar='AGENT',
        help='Original coding agent (forwarded as metadata)',
    )

    run_parser = subparsers.add_parser('run', help='Run a workflow recipe')
    run_parser.add_argument('workflow', help='Workflow name or YAML path')
    list_parser = subparsers.add_parser('list', help='List runtime assets')
    list_subparsers = list_parser.add_subparsers(dest='list_command', required=True)
    list_subparsers.add_parser('agents', help='List available agents')
    list_subparsers.add_parser('workflows', help='List available workflows')
    subparsers.add_parser('status', help='Show system status')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    slugger = Slugger(Bootstrap(Path(__file__).resolve().parent.parent).build())
    if args.command == 'build':
        project_input = ProjectInput(
            idea=args.idea,
            platform=Platform(args.platform),
            coding_agent=CodingAgent(args.coding_agent),
        )
        result = slugger.build(project_input, workflow=args.workflow)
        print(json.dumps({
            'run_id': result.run_id,
            'idea': project_input.idea,
            'platform': project_input.platform.value,
            'coding_agent': project_input.coding_agent.value,
            'workflow': result.definition.name,
            'status': result.status,
            'artifacts': len(result.artifacts),
        }))
        return 0
    if args.command == 'resume':
        project_input = None
        if args.idea and args.platform:
            project_input = ProjectInput(
                idea=args.idea,
                platform=Platform(args.platform),
                coding_agent=CodingAgent(args.coding_agent) if args.coding_agent else CodingAgent.CODEX,
            )
        result = slugger.resume(args.run_id, project_input=project_input)
        print(json.dumps({
            'run_id': result.run_id,
            'workflow': result.definition.name,
            'status': result.status,
            'artifacts': len(result.artifacts),
        }))
        return 0
    if args.command == 'run':
        result = slugger.run_workflow(args.workflow)
        print(json.dumps({'workflow': result.definition.name, 'status': result.status, 'artifacts': len(result.artifacts)}))
        return 0
    if args.command == 'list' and args.list_command == 'agents':
        print('\n'.join(slugger.list_agents()))
        return 0
    if args.command == 'list' and args.list_command == 'workflows':
        print('\n'.join(slugger.list_workflows()))
        return 0
    if args.command == 'status':
        print(json.dumps(slugger.status(), indent=2))
        return 0
    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
