"""Prompt evaluation regression tests and CI quality gates (Task 039)."""

from __future__ import annotations

from pathlib import Path

import pytest

from validators import PromptEvaluationResult, PromptEvaluator, PromptTemplateValidator

_TEMPLATE_DIR = Path('prompts/templates')

# ---------------------------------------------------------------------------
# Variables used when rendering each template for evaluation
# ---------------------------------------------------------------------------

_VARIABLES: dict[str, dict[str, str]] = {
    'agent-system-prompt': {
        'agent_name': 'RequirementsAgent',
        'responsibility': 'convert product vision into structured requirements',
        'inputs': '- Product vision document',
        'outputs': '- Structured requirements document',
        'constraints': '- Must be actionable and testable',
        'quality_criteria': '- All requirements must have acceptance criteria',
    },
    'requirements-prompt': {
        'product_vision': '# Product Vision\n\nBuild a todo list app.',
    },
    'architecture-prompt': {
        'requirements': '- Support CRUD operations for tasks',
        'constraints': '- Must deploy on a single server',
    },
    'code-review-prompt': {
        'changed_artifacts': 'src/app/main.py',
        'requirements_context': 'User story: manage tasks',
    },
}

# Required headings / substrings present in each template after rendering
_REQUIRED_SECTIONS: dict[str, list[str]] = {
    'agent-system-prompt': ['RequirementsAgent', 'Inputs', 'Expected Outputs', 'Constraints', 'Quality Criteria'],
    'requirements-prompt': ['Product Vision', 'todo list app', 'Scope', 'Functional requirements', 'Acceptance criteria'],
    'architecture-prompt': ['Architectural goals', 'Technology choices', 'CRUD operations', 'single server'],
    'code-review-prompt': ['Summary', 'Findings', 'main.py', 'manage tasks'],
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def evaluator() -> PromptEvaluator:
    return PromptEvaluator(_TEMPLATE_DIR)


# ---------------------------------------------------------------------------
# Structural / discovery tests
# ---------------------------------------------------------------------------

class TestPromptTemplateDiscovery:
    def test_template_directory_exists(self) -> None:
        assert _TEMPLATE_DIR.is_dir()

    def test_known_templates_present(self, evaluator: PromptEvaluator) -> None:
        templates = evaluator.list_templates()
        for name in ('agent-system-prompt', 'requirements-prompt', 'architecture-prompt', 'code-review-prompt'):
            assert name in templates, f'Expected template {name!r} not found'

    def test_load_template_returns_non_empty_string(self, evaluator: PromptEvaluator) -> None:
        for name in evaluator.list_templates():
            text = evaluator.load_template(name)
            assert isinstance(text, str) and len(text.strip()) > 0, f'Template {name!r} is empty'

    def test_load_missing_template_raises_file_not_found(self, evaluator: PromptEvaluator) -> None:
        with pytest.raises(FileNotFoundError):
            evaluator.load_template('nonexistent-template')


# ---------------------------------------------------------------------------
# Placeholder extraction tests
# ---------------------------------------------------------------------------

class TestPlaceholderExtraction:
    def test_agent_system_prompt_placeholders(self, evaluator: PromptEvaluator) -> None:
        placeholders = evaluator.extract_placeholders('agent-system-prompt')
        for expected in ('agent_name', 'responsibility', 'inputs', 'outputs', 'constraints', 'quality_criteria'):
            assert expected in placeholders

    def test_requirements_prompt_placeholders(self, evaluator: PromptEvaluator) -> None:
        assert 'product_vision' in evaluator.extract_placeholders('requirements-prompt')

    def test_architecture_prompt_placeholders(self, evaluator: PromptEvaluator) -> None:
        placeholders = evaluator.extract_placeholders('architecture-prompt')
        assert 'requirements' in placeholders
        assert 'constraints' in placeholders

    def test_code_review_prompt_placeholders(self, evaluator: PromptEvaluator) -> None:
        placeholders = evaluator.extract_placeholders('code-review-prompt')
        assert 'changed_artifacts' in placeholders
        assert 'requirements_context' in placeholders

    def test_extract_placeholders_deduplicates(self, evaluator: PromptEvaluator, tmp_path: Path) -> None:
        dup_template = tmp_path / 'dup.md'
        dup_template.write_text('{{ foo }} and {{ foo }} again, {{ bar }}', encoding='utf-8')
        ev = PromptEvaluator(tmp_path)
        assert ev.extract_placeholders('dup') == ['foo', 'bar']


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------

class TestPromptRendering:
    def test_variables_substituted_in_output(self, evaluator: PromptEvaluator) -> None:
        for name, variables in _VARIABLES.items():
            rendered = evaluator.render(name, variables)
            for value in variables.values():
                assert value in rendered, f'Variable value {value!r} not found in rendered {name!r}'

    def test_unresolved_placeholders_remain_when_variable_missing(self, evaluator: PromptEvaluator) -> None:
        rendered = evaluator.render('requirements-prompt', {})
        assert '{{ product_vision }}' in rendered

    def test_extra_variables_ignored(self, evaluator: PromptEvaluator) -> None:
        variables = dict(_VARIABLES['requirements-prompt'])
        variables['extra_key'] = 'should_be_ignored'
        rendered = evaluator.render('requirements-prompt', variables)
        assert 'should_be_ignored' not in rendered


# ---------------------------------------------------------------------------
# Quality gate / validation tests
# ---------------------------------------------------------------------------

class TestPromptQualityGates:
    @pytest.mark.parametrize('template_name', list(_VARIABLES.keys()))
    def test_fully_rendered_prompt_passes_default_validator(
        self,
        evaluator: PromptEvaluator,
        template_name: str,
    ) -> None:
        result = evaluator.evaluate(template_name, _VARIABLES[template_name])
        assert result.validation.valid, (
            f'Template {template_name!r} failed validation: '
            + ', '.join(e.message for e in result.validation.errors)
        )

    @pytest.mark.parametrize('template_name', list(_REQUIRED_SECTIONS.keys()))
    def test_rendered_prompt_contains_required_sections(
        self,
        evaluator: PromptEvaluator,
        template_name: str,
    ) -> None:
        sections = _REQUIRED_SECTIONS[template_name]
        result = evaluator.evaluate(template_name, _VARIABLES[template_name], extra_sections=sections)
        assert result.validation.valid, (
            f'Template {template_name!r} missing required sections: '
            + ', '.join(e.message for e in result.validation.errors)
        )

    def test_empty_rendered_prompt_fails_validation(self, tmp_path: Path) -> None:
        (tmp_path / 'empty.md').write_text('   ', encoding='utf-8')
        ev = PromptEvaluator(tmp_path, PromptTemplateValidator(min_length=10))
        result = ev.evaluate('empty', {})
        assert not result.validation.valid

    def test_missing_required_section_fails_validation(self, tmp_path: Path) -> None:
        (tmp_path / 'minimal.md').write_text('Hello world', encoding='utf-8')
        ev = PromptEvaluator(tmp_path, PromptTemplateValidator(required_sections=['MISSING']))
        result = ev.evaluate('minimal', {}, extra_sections=['ALSO_MISSING'])
        assert not result.validation.valid
        messages = [e.message for e in result.validation.errors]
        assert any('MISSING' in m for m in messages)


# ---------------------------------------------------------------------------
# PromptEvaluationResult contract tests
# ---------------------------------------------------------------------------

class TestPromptEvaluationResult:
    def test_result_reports_missing_variables(self, evaluator: PromptEvaluator) -> None:
        result = evaluator.evaluate('requirements-prompt', {})
        assert 'product_vision' in result.missing_variables

    def test_result_reports_no_missing_variables_when_all_supplied(self, evaluator: PromptEvaluator) -> None:
        result = evaluator.evaluate('requirements-prompt', _VARIABLES['requirements-prompt'])
        assert result.missing_variables == []

    def test_result_contains_rendered_text(self, evaluator: PromptEvaluator) -> None:
        result = evaluator.evaluate('requirements-prompt', _VARIABLES['requirements-prompt'])
        assert 'todo list app' in result.rendered

    def test_result_template_name_matches_input(self, evaluator: PromptEvaluator) -> None:
        result = evaluator.evaluate('requirements-prompt', {})
        assert result.template_name == 'requirements-prompt'


# ---------------------------------------------------------------------------
# evaluate_all regression sweep (CI gate)
# ---------------------------------------------------------------------------

class TestEvaluateAllRegressionSweep:
    """Regression gate: every template must pass default validation when
    supplied with its canonical variables.  This test acts as a CI quality
    gate to prevent prompt degradation."""

    def test_all_templates_pass_with_canonical_variables(self, evaluator: PromptEvaluator) -> None:
        results = evaluator.evaluate_all(_VARIABLES)
        failures = {
            name: [e.message for e in r.validation.errors]
            for name, r in results.items()
            if not r.validation.valid
        }
        assert not failures, f'Prompt quality gate failures: {failures}'

    def test_all_templates_produce_non_empty_renders(self, evaluator: PromptEvaluator) -> None:
        results = evaluator.evaluate_all(_VARIABLES)
        for name, result in results.items():
            assert result.rendered.strip(), f'Template {name!r} rendered to empty string'
