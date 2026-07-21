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
    assert inputs["target_repository"]["required"] is True
    assert inputs["target_repository"]["type"] == "string"
    assert "sandbox repository" in inputs["target_repository"]["description"]
    assert (
        inputs["target_repository"]["default"]
        == "Young-Consultations/slugger-generated-demos"
    )
    assert inputs["target_repository"]["default"] != "${{ github.repository }}"
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
    assert "TARGET_REPOSITORY: ${{ inputs.target_repository }}" in text
    assert '--repo "$TARGET_REPOSITORY"' in text
    assert '--repo "${{ github.repository }}"' not in text
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


def test_user_idea_workflow_publishes_in_verifier_job_with_least_privilege() -> None:
    data = _workflow()
    jobs = data["jobs"]
    verify = jobs["verify-generated-demo"]
    assert verify["permissions"] == {"contents": "write", "pull-requests": "write"}
    assert all(
        job.get("permissions", {"contents": "read"}) == {"contents": "read"}
        for name, job in jobs.items()
        if name != "verify-generated-demo"
    )
    assert "publish-verified-draft-pr" not in jobs
    assert "python -m cli.main mvp publish" in str(verify)
    assert "verify_protected_manifest" in str(verify)
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "${{ secrets.SLUGGER_GITHUB_TOKEN }}" in str(verify)
    assert text.count("${{ secrets.SLUGGER_GITHUB_TOKEN }}") == 2
    assert "${{ github.token }}" not in text
    assert "cp -R verified-artifact/slugger-home" not in str(verify)
    assert "mvp-artifact/slugger-home" not in str(verify)


def test_target_repository_is_validated_before_codex_generation() -> None:
    data = _workflow()
    prepare = data["jobs"]["prepare-codex-input"]
    generate = data["jobs"]["generate-with-codex"]
    assert "needs" not in prepare
    assert generate["needs"] == "prepare-codex-input"
    assert "Validate target repository before Codex" in str(prepare)
    assert "api.github.com" in str(prepare)
    validate = next(
        step
        for step in prepare["steps"]
        if step["name"] == "Validate target repository before Codex"
    )
    assert validate["env"]["GH_TOKEN"] == "${{ secrets.SLUGGER_GITHUB_TOKEN }}"
    assert validate["env"]["TARGET_BASE_BRANCH"] == "main"
    assert "not empty and is not Slugger-managed" in str(prepare)


def test_success_artifact_contains_only_publication_outputs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "publication-summary.json" in text
    assert "mvp-artifact/slugger-home" not in text
    assert "slugger-build-summary.json mvp-artifact" not in text
    assert "Forbidden artifact content" in text
    assert all(
        forbidden in text for forbidden in [".venv", "__pycache__", ".pytest_cache"]
    )


def test_restricted_verification_evidence_stays_outside_generated_tree() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'PROJECT_DIR="downloaded-artifact/generated-demo"' in text
    assert 'WORKSPACE_ROOT="downloaded-artifact"' in text
    assert '--evidence-file "$WORKSPACE_ROOT/verification-evidence.json"' in text
    assert '--evidence-file "$PROJECT_DIR/verification-evidence.json"' not in text
    assert (
        "cp downloaded-artifact/verification-evidence.json mvp-artifact/verification-evidence.json"
        in text
    )
    assert "downloaded-artifact/verification-evidence.json" in text
    assert "downloaded-artifact/generated-demo/verification-evidence.json" not in text


def test_pre_publication_failures_emit_sanitized_diagnostics() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert ": > publication-error.log" in text
    assert "write_publication_diagnostic" in text
    assert 'write_publication_diagnostic "pre_publication_token"' in text
    assert 'write_publication_diagnostic "pre_publication_manifest"' in text
    assert "Pre-publication manifest or summary check failed" in text
    assert "publication-diagnostics.json" in text
