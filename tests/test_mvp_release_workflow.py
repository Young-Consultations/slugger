from pathlib import Path

import yaml


WORKFLOW = Path(".github/workflows/real-codex-cli-demo.yml")
README = Path("README.md")
CHECKLIST = Path("docs/mvp-release-checklist.md")


def test_mvp_workflow_has_single_manual_trigger_and_real_codex_path() -> None:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    triggers = data.get("on", data.get(True))
    assert set(triggers) == {"workflow_dispatch"}
    assert data["permissions"] == {"contents": "read"}
    jobs = data["jobs"]
    assert list(jobs) == [
        "prepare-codex-input",
        "generate-with-codex",
        "prepare-generated-artifact",
        "verify-generated-demo",
    ]
    generation_steps = jobs["generate-with-codex"]["steps"]
    assert any(
        step.get("uses", "").startswith("openai/codex-action@")
        for step in generation_steps
    )
    assert "environment" in jobs["generate-with-codex"]
    assert jobs["generate-with-codex"]["environment"] == "codex-demo"


def test_mvp_workflow_uploads_success_artifact_and_failure_diagnostics() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "slugger-mvp-cli-demo-${{ github.run_id }}" in text
    assert "slugger-codex-certification-${{ github.run_id }}" in text
    assert "MVP_ARTIFACT_README.md" in text
    assert "verification-evidence.json" in text
    assert "python -m hello_codex.main greet Joseph" in text
    assert "Hello, Joseph!" in text


def test_success_artifact_keeps_generated_demo_manifest_clean() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "cp downloaded-artifact/generated-demo/verification-evidence.json mvp-artifact/verification-evidence.json" in text
    assert "rm -f mvp-artifact/generated-demo/verification-evidence.json" in text
    assert 'verify_protected_manifest(Path("mvp-artifact/generated-demo"), Path("mvp-artifact/generated-project-manifest.json"))' in text


def test_mvp_release_documentation_names_supported_path_and_limitations() -> None:
    readme = README.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")

    assert "single supported MVP release path" in readme
    assert "OPENAI_API_KEY" in readme
    assert "slugger-mvp-cli-demo-<run_id>" in readme
    assert "Known limitations" in checklist
    assert "v0.1.0" in checklist
