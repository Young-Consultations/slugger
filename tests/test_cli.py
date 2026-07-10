"""Tests for CLI argument parsing and the build command."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli.main import build_parser, main
from models.project import CodingAgent, Platform, ProjectInput


# ---------------------------------------------------------------------------
# ProjectInput model tests
# ---------------------------------------------------------------------------

class TestProjectInput:
    def test_defaults_coding_agent_to_codex(self) -> None:
        pi = ProjectInput(idea='A social media app', platform=Platform.WEB)
        assert pi.coding_agent is CodingAgent.CODEX

    def test_as_metadata_returns_plain_strings(self) -> None:
        pi = ProjectInput(idea='Todo list app', platform=Platform.IOS, coding_agent=CodingAgent.ANTHROPIC)
        meta = pi.as_metadata()
        assert meta == {'idea': 'Todo list app', 'platform': 'ios', 'coding_agent': 'anthropic'}

    def test_as_metadata_codex_default(self) -> None:
        pi = ProjectInput(idea='News reader', platform=Platform.ANDROID)
        meta = pi.as_metadata()
        assert meta['coding_agent'] == 'codex'
        assert meta['platform'] == 'android'


# ---------------------------------------------------------------------------
# Platform and CodingAgent enum tests
# ---------------------------------------------------------------------------

class TestEnums:
    def test_platform_values(self) -> None:
        assert {p.value for p in Platform} == {'ios', 'android', 'web'}

    def test_coding_agent_values(self) -> None:
        assert {a.value for a in CodingAgent} == {'codex', 'anthropic'}


# ---------------------------------------------------------------------------
# CLI argument parser tests
# ---------------------------------------------------------------------------

class TestBuildParser:
    def setup_method(self) -> None:
        self.parser = build_parser()

    def test_build_requires_idea_and_platform(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(['build', '--platform', 'ios'])

    def test_build_requires_platform(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(['build', 'My app idea'])

    def test_build_parses_all_arguments(self) -> None:
        args = self.parser.parse_args([
            'build', 'A todo app',
            '--platform', 'web',
            '--coding-agent', 'anthropic',
        ])
        assert args.command == 'build'
        assert args.idea == 'A todo app'
        assert args.platform == 'web'
        assert args.coding_agent == 'anthropic'
        assert args.workflow is None

    def test_build_defaults_coding_agent_to_codex(self) -> None:
        args = self.parser.parse_args(['build', 'An idea', '--platform', 'android'])
        assert args.coding_agent == 'codex'

    def test_build_accepts_workflow_override(self) -> None:
        args = self.parser.parse_args([
            'build', 'An idea',
            '--platform', 'ios',
            '--workflow', 'requirements-gathering',
        ])
        assert args.workflow == 'requirements-gathering'

    def test_build_rejects_invalid_platform(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(['build', 'An idea', '--platform', 'windows'])

    def test_build_rejects_invalid_coding_agent(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(['build', 'An idea', '--platform', 'web', '--coding-agent', 'gemini'])

    def test_run_subcommand_still_works(self) -> None:
        args = self.parser.parse_args(['run', 'full-sdlc'])
        assert args.command == 'run'
        assert args.workflow == 'full-sdlc'


# ---------------------------------------------------------------------------
# main() integration smoke test (mocked Slugger)
# ---------------------------------------------------------------------------

class TestMainBuildCommand:
    def _make_fake_result(self, workflow_name: str = 'full-sdlc', status: str = 'succeeded') -> MagicMock:
        result = MagicMock()
        result.definition.name = workflow_name
        result.status = status
        result.artifacts = []
        return result

    @patch('cli.main.Bootstrap')
    def test_build_command_returns_zero(self, mock_bootstrap: MagicMock, capsys) -> None:
        fake_slugger = MagicMock()
        fake_slugger.build.return_value = self._make_fake_result()
        mock_bootstrap.return_value.build.return_value = MagicMock()
        with patch('cli.main.Slugger', return_value=fake_slugger):
            rc = main(['build', 'A cool app', '--platform', 'web'])
        assert rc == 0

    @patch('cli.main.Bootstrap')
    def test_build_command_output_includes_idea_and_platform(self, mock_bootstrap: MagicMock, capsys) -> None:
        fake_slugger = MagicMock()
        fake_slugger.build.return_value = self._make_fake_result()
        mock_bootstrap.return_value.build.return_value = MagicMock()
        with patch('cli.main.Slugger', return_value=fake_slugger):
            main(['build', 'My social app', '--platform', 'ios'])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['idea'] == 'My social app'
        assert output['platform'] == 'ios'
        assert output['coding_agent'] == 'codex'

    @patch('cli.main.Bootstrap')
    def test_build_command_forwards_project_input_to_slugger(self, mock_bootstrap: MagicMock) -> None:
        fake_slugger = MagicMock()
        fake_slugger.build.return_value = self._make_fake_result()
        mock_bootstrap.return_value.build.return_value = MagicMock()
        with patch('cli.main.Slugger', return_value=fake_slugger):
            main(['build', 'Chat app', '--platform', 'android', '--coding-agent', 'anthropic'])
        call_args = fake_slugger.build.call_args
        project_input = call_args[0][0]
        assert isinstance(project_input, ProjectInput)
        assert project_input.idea == 'Chat app'
        assert project_input.platform is Platform.ANDROID
        assert project_input.coding_agent is CodingAgent.ANTHROPIC

    @patch('cli.main.Bootstrap')
    def test_build_command_forwards_workflow_override(self, mock_bootstrap: MagicMock) -> None:
        fake_slugger = MagicMock()
        fake_slugger.build.return_value = self._make_fake_result('requirements-gathering')
        mock_bootstrap.return_value.build.return_value = MagicMock()
        with patch('cli.main.Slugger', return_value=fake_slugger):
            main(['build', 'Blog engine', '--platform', 'web', '--workflow', 'requirements-gathering'])
        call_kwargs = fake_slugger.build.call_args[1]
        assert call_kwargs.get('workflow') == 'requirements-gathering'
