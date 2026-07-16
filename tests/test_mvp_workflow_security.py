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
    assert "secrets.OPENAI_API_KEY" in str(codex)
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
    assert "write_manifest" in str(data["jobs"]["prepare-generated-artifact"])
    assert "--container" in str(data["jobs"]["verify-generated-demo"])
    assert data["jobs"]["verify-generated-demo"]["permissions"] == {"contents": "read"}


def test_evidence_uploads_always_and_jobs_have_timeouts() -> None:
    data = _workflow()
    assert all("timeout-minutes" in job for job in data["jobs"].values())
    verify_steps = data["jobs"]["verify-generated-demo"]["steps"]
    upload = next(
        step for step in verify_steps if step["name"] == "Upload verification evidence"
    )
    assert upload["if"] == "always()"
