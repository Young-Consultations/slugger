"""Command line interface for Slugger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from orchestrator import Bootstrap, Slugger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='slugger', description='Slugger AI Software Factory CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)
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
