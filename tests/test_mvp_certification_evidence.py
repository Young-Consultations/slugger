import json
from pathlib import Path
import subprocess
import sys

RUN_DIR = Path("docs/certification/runs/29460251536")


def test_baseline_certification_record_present_and_sanitized() -> None:
    assert (RUN_DIR / "certification-summary.md").is_file()
    evidence = json.loads(
        (RUN_DIR / "verification-evidence.json").read_text(encoding="utf-8")
    )
    assert evidence["workflow_run_id"] == "29460251536"
    assert evidence["certification_classification"]["Functional MVP"] == "Passed"
    text = "\n".join(
        p.read_text(encoding="utf-8") for p in RUN_DIR.iterdir() if p.is_file()
    )
    for forbidden in ("OPENAI_API_KEY", "ghp_", "Authorization:", "Bearer "):
        assert forbidden not in text


def test_certification_record_script_is_deterministic(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.json"
    manifest = tmp_path / "manifest.json"
    evidence.write_text(
        json.dumps({"workflow_name": "W", "final_status": "passed"}), encoding="utf-8"
    )
    manifest.write_text(
        json.dumps({"manifest_version": 1, "entries": []}), encoding="utf-8"
    )
    out = tmp_path / "out"
    cmd = [
        sys.executable,
        "scripts/create_certification_record.py",
        "--run-id",
        "1",
        "--evidence",
        str(evidence),
        "--manifest",
        str(manifest),
        "--output-root",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    first = (out / "1" / "verification-evidence.json").read_text(encoding="utf-8")
    subprocess.run(cmd, check=True)
    second = (out / "1" / "verification-evidence.json").read_text(encoding="utf-8")
    assert first == second
