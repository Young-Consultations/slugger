"""Fail when tracked text files contain obsolete GitHub namespace references."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

OBSOLETE = "mighty" + "joe909"
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
SKIP_SUFFIXES = {
    ".7z",
    ".a",
    ".bin",
    ".bmp",
    ".bz2",
    ".class",
    ".dll",
    ".dylib",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".pyo",
    ".so",
    ".tar",
    ".tgz",
    ".webp",
    ".whl",
    ".xz",
    ".zip",
}
# No obsolete namespace references are currently active or historically exempt.
EXCEPTIONS: set[tuple[str, int]] = set()


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"])
    return [Path(raw.decode("utf-8")) for raw in output.split(b"\0") if raw]


def should_skip(path: Path) -> bool:
    return (
        bool(SKIP_PARTS.intersection(path.parts))
        or path.suffix.lower() in SKIP_SUFFIXES
    )


def main() -> int:
    findings: list[str] = []
    for path in tracked_files():
        if should_skip(path) or not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            if (
                OBSOLETE.lower() in line.lower()
                and (str(path), number) not in EXCEPTIONS
            ):
                findings.append(f"{path}:{number}:{line}")
    if findings:
        print("Obsolete namespace references found:", file=sys.stderr)
        print("\n".join(findings), file=sys.stderr)
        return 1
    print("No obsolete namespace references found in tracked text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
