from pathlib import Path

import yaml

WORKFLOW = Path(".github/workflows/user-idea-codex-cli-demo.yml")


def _workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_user_idea_workflow_accepts_manual_idea_input() -> None:
    data = _workflow()
    trigger = data[True]["workflow_dispatch"]
    inputs = trigger["inputs"]
    assert inputs["idea"]["required"] is True
    assert inputs["idea"]["type"] == "string"
    assert inputs["project_name"]["required"] is True
    assert "normalized to lowercase kebab-case" in inputs["project_name"]["description"]
    assert "hello-codex is reserved" in inputs["project_name"]["description"]
    assert inputs["project_name"]["default"] == "user-idea-cli"
    assert inputs["retain_diagnostics"]["type"] == "boolean"


def test_user_idea_workflow_renders_prompt_from_safe_inputs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    data = _workflow()
    prepare = data["jobs"]["prepare-codex-input"]
    assert prepare["outputs"] == {
        "project_name": "${{ steps.idea_inputs.outputs.project_name }}",
        "package_name": "${{ steps.idea_inputs.outputs.package_name }}",
    }
    assert "normalize_project_name(submitted_project_name)" in text
    assert 'prompt_inputs(normalized_project_name, os.environ["USER_IDEA"])' in text
    assert "render_demo_prompt(" in text
    assert "USER_IDEA: ${{ inputs.idea }}" in text
    assert "PROJECT_NAME: ${{ inputs.project_name }}" in text
    assert "GITHUB_STEP_SUMMARY" in text
    assert "Submitted project name" in text
    assert "Normalized project name" in text


def test_user_idea_workflow_uses_dynamic_project_for_verification() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert '--name "${{ needs.prepare-codex-input.outputs.project_name }}"' in text
    assert (
        '--repo "local/${{ needs.prepare-codex-input.outputs.project_name }}"' in text
    )
    assert "PROJECT_NAME: ${{ needs.prepare-codex-input.outputs.project_name }}" in text
    assert "BUILD_IDEA: ${{ inputs.idea }}" in text
    assert '"$BUILD_IDEA"' in text
    assert (
        "python -m ${{ needs.prepare-codex-input.outputs.package_name }}.main --help"
        in text
    )
    assert "slugger-user-idea-cli-demo-${{ github.run_id }}" in text


def test_user_idea_certification_downloads_only_available_diagnostics() -> None:
    data = _workflow()
    steps = data["jobs"]["publish-certification-diagnostics"]["steps"]
    generated = next(
        step
        for step in steps
        if step["name"] == "Download generated artifact diagnostics"
    )
    verifier = next(
        step for step in steps if step["name"] == "Download verifier diagnostics"
    )
    assert generated["if"] == "needs.prepare-generated-artifact.result == 'success'"
    assert verifier["if"] == "needs.verify-generated-demo.result != 'skipped'"
    assert generated["continue-on-error"] is True
    assert verifier["continue-on-error"] is True
