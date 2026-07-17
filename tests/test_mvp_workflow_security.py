import re
from pathlib import Path

import yaml

WORKFLOW = Path(".github/workflows/real-codex-cli-demo.yml")


def _workflow():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_workflow_is_manual_only_and_has_concurrency() -> None:
    data = _workflow()
    assert list(data[True].keys()) == ["workflow_dispatch"]
    assert data["concurrency"]["cancel-in-progress"] is False


def test_openai_key_only_in_codex_job() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert text.count("secrets.OPENAI_API_KEY") == 1
    data = _workflow()
    codex = data["jobs"]["generate-with-codex"]
    assert codex["environment"] == "codex-demo"
    assert "secrets.OPENAI_API_KEY" in str(codex)
    assert "python -m" not in str(codex)
    for name, job in data["jobs"].items():
        if name != "generate-with-codex":
            assert "secrets.OPENAI_API_KEY" not in str(job)


def test_actions_are_pinned_to_immutable_shas() -> None:
    for match in re.finditer(
        r"uses: ([^@\s]+)@([^\s#]+)", WORKFLOW.read_text(encoding="utf-8")
    ):
        assert re.fullmatch(r"[0-9a-f]{40}", match.group(2)), match.group(0)


def test_manifest_and_container_verification_are_in_fresh_jobs() -> None:
    data = _workflow()
    assert "generate-with-codex" in data["jobs"]
    assert "prepare-generated-artifact" in data["jobs"]
    assert "verify-generated-demo" in data["jobs"]
    assert "write_manifest" not in str(data["jobs"]["generate-with-codex"])
    assert "write_protected_manifest" in str(data["jobs"]["prepare-generated-artifact"])
    assert "sanitize_protected_artifact" in str(
        data["jobs"]["prepare-generated-artifact"]
    )
    assert "--container" in str(data["jobs"]["verify-generated-demo"])
    assert data["jobs"]["verify-generated-demo"]["permissions"] == {"contents": "read"}


def test_evidence_uploads_always_and_jobs_have_timeouts() -> None:
    data = _workflow()
    assert all("timeout-minutes" in job for job in data["jobs"].values())
    verify_steps = data["jobs"]["verify-generated-demo"]["steps"]
    upload = next(
        step
        for step in verify_steps
        if step["name"] == "Upload sanitized certification evidence"
    )
    certification = next(
        step
        for step in verify_steps
        if step["name"] == "Produce sanitized certification evidence"
    )
    assert upload["if"] == "always()"
    assert certification["if"] == "always()"


def test_restricted_verification_uses_sanitized_artifact_not_build_workspace() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'PROJECT_DIR="downloaded-artifact/generated-demo"' in text
    assert 'WORKSPACE_ROOT="downloaded-artifact"' in text
    assert "PROJECT_NAME: hello-codex" in text
    assert '--project-name "$PROJECT_NAME"' in text
    assert '--evidence-file "$PROJECT_DIR/verification-evidence.json"' in text
    assert 'print(data["workspace_path"])' not in text
    assert 'print(Path(data["workspace_path"]).parent)' not in text


def test_verify_job_runs_exactly_one_authoritative_slugger_build() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    data = _workflow()
    verify_job = data["jobs"]["verify-generated-demo"]
    assert str(verify_job).count("python -m cli.main mvp build") == 1
    assert text.count("python -m cli.main mvp build") == 1
    assert "${{ github.workspace }}/.slugger-demo" not in text
    authoritative = next(
        step
        for step in verify_job["steps"]
        if step["name"] == "Run Slugger service with artifact adapter"
    )
    assert authoritative["env"]["SLUGGER_HOME"] == "${{ runner.temp }}/slugger-home"
    assert authoritative["env"]["SLUGGER_MVP_SKIP_PUBLISH"] == "1"
    assert (
        authoritative["env"]["SLUGGER_MVP_ARTIFACT_DIR"]
        == "${{ github.workspace }}/downloaded-artifact/generated-demo"
    )
    assert (
        authoritative["env"]["SLUGGER_MVP_ARTIFACT_MANIFEST"]
        == "${{ github.workspace }}/downloaded-artifact/generated-project-manifest.json"
    )


def test_build_summary_is_validated_atomically_without_tee() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "tee slugger-build-summary.json" not in text
    assert "> slugger-build-summary.tmp.json" in text
    assert "2> slugger-build-error.log" in text
    assert "python -m json.tool slugger-build-summary.tmp.json >/dev/null" in text
    assert "mv slugger-build-summary.tmp.json slugger-build-summary.json" in text


def test_authoritative_build_result_is_fully_asserted() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'data["status"] in {"ready_to_publish", "completed"}' in text
    assert 'data["publication_skipped"] is True' in text
    assert 'data["validation_passed"] is True' in text
    assert 'data["test_passed"] is True' in text
    assert 'data["smoke_passed"] is True' in text
    assert 'data["functional_passed"] is True' in text
    assert "verify_protected_manifest" in text


def test_exactly_one_canonical_real_codex_workflow_exists() -> None:
    workflows = sorted(Path(".github/workflows").glob("real-codex*.yml"))
    assert workflows == [WORKFLOW]


def test_slugger_artifact_adapter_and_exact_function_are_required() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "SLUGGER_MVP_ARTIFACT_DIR" in text
    assert "SLUGGER_MVP_ARTIFACT_MANIFEST" in text
    assert "python -m hello_codex.main greet Joseph" in text
    assert "Hello, Joseph!" in text
    assert "slugger-codex-certification-${{ github.run_id }}" in text
