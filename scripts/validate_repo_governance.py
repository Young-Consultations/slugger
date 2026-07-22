"""Validate Slugger repository governance and decoupling invariants."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
]
PINNED = re.compile(r"uses:\s*[^\s]+@[0-9a-f]{40}(?:\s+#.*)?\s*$")
USES = re.compile(r"uses:\s*([^\s]+)")


def fail(message: str) -> None:
    raise AssertionError(message)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    )


def validate_required_files() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail(f"Missing governance files: {missing}")


def validate_no_submodule() -> None:
    if (ROOT / ".gitmodules").exists():
        fail(".gitmodules remains; generated demos must not be a submodule")
    status = git("submodule", "status").strip()
    if status:
        fail(f"Unexpected git submodule status: {status}")
    if (ROOT / "slugger-generated-demos").exists():
        fail("slugger-generated-demos checkout remains in the Slugger repository")


def validate_namespace_references() -> None:
    try:
        output = git("grep", "-In", "mightyjoe909", "--", ".")
    except subprocess.CalledProcessError as exc:
        if exc.returncode == 1:
            output = ""
        else:
            raise
    offenders = [
        line
        for line in output.splitlines()
        if "mighty" + "joe909" not in line and "historical" not in line.lower()
    ]
    if offenders:
        fail("Obsolete namespace references remain: " + repr(offenders[:5]))


def validate_workflows() -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "permissions:" not in text:
            fail(f"Workflow lacks explicit permissions: {path.relative_to(ROOT)}")
        if "pull_request_target" in text:
            fail(f"Unsafe pull_request_target trigger found: {path.relative_to(ROOT)}")
        for line in text.splitlines():
            match = USES.search(line)
            if match and match.group(1).startswith("./.github/workflows/"):
                continue
            if match and not PINNED.search(line):
                fail(f"Unpinned action in {path.relative_to(ROOT)}: {line.strip()}")


def validate_docs_boundaries() -> None:
    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            "README.md",
            "docs/mvp.md",
            "docs/mvp-certification.md",
            "docs/mvp-release-checklist.md",
        ]
    )
    for phrase in ["generation workflow", "certification", "release"]:
        if phrase not in docs:
            fail(
                f"Documentation does not distinguish required workflow phrase: {phrase}"
            )


def main() -> int:
    checks = [
        validate_required_files,
        validate_no_submodule,
        validate_namespace_references,
        validate_workflows,
        validate_docs_boundaries,
    ]
    for check in checks:
        check()
    print("Repository governance validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
