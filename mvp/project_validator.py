"""Generated-project validation for the isolated Slugger MVP path."""

from __future__ import annotations

import ast
import re
import stat
import tomllib
from pathlib import Path

from mvp.integrations.codex import package_name_for_project
from mvp.models import CheckResult, GeneratedProjectInventory, MvpProjectRequest
from mvp.workspace import MvpWorkspace, WorkspaceManager, WorkspaceSafetyError

SECRET_FILENAMES = {".env", ".env.local", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
SECRET_SUFFIXES = (".key", ".pem", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db")
ALLOWED_BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico"}
MAX_FILE_BYTES = 1_000_000
_PACKAGE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class ProjectValidationError(ValueError):
    """Raised when generated project validation fails."""


class ProjectValidator:
    """Validate generated files before installation, testing, or publication."""

    def __init__(self, workspace_manager: WorkspaceManager, *, max_file_bytes: int = MAX_FILE_BYTES) -> None:
        self.workspace_manager = workspace_manager
        self.max_file_bytes = max_file_bytes

    def validate(
        self,
        request: MvpProjectRequest,
        workspace: MvpWorkspace | Path,
        inventory: GeneratedProjectInventory | None = None,
    ) -> tuple[CheckResult, ...]:
        workspace_path = self.workspace_manager._workspace_path(workspace)
        results = [
            self._check_path_safety(workspace_path),
            self._check_content_safety(workspace_path),
            self._check_required_files(request, workspace_path, inventory),
            self._check_python_syntax(workspace_path),
            self._check_pyproject(request, workspace_path),
        ]
        return tuple(results)

    @staticmethod
    def passed(results: tuple[CheckResult, ...]) -> bool:
        return bool(results) and all(result.passed for result in results)

    def require_passed(self, results: tuple[CheckResult, ...]) -> None:
        failures = [result for result in results if not result.passed]
        if failures:
            raise ProjectValidationError("; ".join(f"{r.name}: {r.message}" for r in failures))

    def _check_path_safety(self, workspace_path: Path) -> CheckResult:
        try:
            for path in workspace_path.rglob("*"):
                relative = path.relative_to(workspace_path)
                if "\x00" in relative.as_posix():
                    raise WorkspaceSafetyError("Generated path contains a null byte")
                resolved = path.resolve(strict=True)
                if not resolved.is_relative_to(workspace_path):
                    raise WorkspaceSafetyError(f"Generated path escapes workspace: {relative}")
                if not path.is_symlink() and not stat.S_ISREG(path.lstat().st_mode) and not path.is_dir():
                    raise WorkspaceSafetyError(f"Generated path is not a regular file or directory: {relative}")
            return CheckResult("path_safety", True, "All generated paths stay within the workspace")
        except (OSError, WorkspaceSafetyError) as exc:
            return CheckResult("path_safety", False, str(exc))

    def _check_content_safety(self, workspace_path: Path) -> CheckResult:
        try:
            for path in workspace_path.rglob("*"):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(workspace_path).as_posix()
                name = path.name.lower()
                suffix = path.suffix.lower()
                if name in SECRET_FILENAMES or suffix in SECRET_SUFFIXES or "private key" in name:
                    return CheckResult("content_safety", False, f"Prohibited generated file: {relative}")
                size = path.stat().st_size
                if size > self.max_file_bytes:
                    return CheckResult("content_safety", False, f"Generated file exceeds size limit: {relative}")
                data = path.read_bytes()
                if b"-----BEGIN " in data and b"PRIVATE KEY-----" in data:
                    return CheckResult("content_safety", False, f"Private key material detected: {relative}")
                if b"\x00" in data and suffix not in ALLOWED_BINARY_SUFFIXES:
                    return CheckResult("content_safety", False, f"Unsupported binary file: {relative}")
            return CheckResult("content_safety", True, "No prohibited generated content detected")
        except OSError as exc:
            return CheckResult("content_safety", False, str(exc))

    def _check_required_files(self, request: MvpProjectRequest, workspace_path: Path, inventory: GeneratedProjectInventory | None) -> CheckResult:
        package_name = package_name_for_project(request.project_name)
        required = ["README.md", "pyproject.toml", f"src/{package_name}/__init__.py"]
        paths = {p.relative_to(workspace_path).as_posix() for p in workspace_path.rglob("*") if p.is_file()}
        missing = [path for path in required if path not in paths]
        source_files = [path for path in paths if path.startswith("src/") and path.endswith(".py")]
        test_files = [path for path in paths if path.startswith("tests/") and path.endswith(".py")]
        if missing or not source_files or not test_files:
            return CheckResult("required_files", False, "Missing required generated project files", {"missing": missing, "source_files": source_files, "test_files": test_files})
        if inventory is not None and not inventory.files:
            return CheckResult("required_files", False, "Inventory is empty")
        return CheckResult("required_files", True, "Required generated project files are present", {"file_count": len(paths)})

    def _check_python_syntax(self, workspace_path: Path) -> CheckResult:
        for path in sorted(workspace_path.rglob("*.py")):
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                return CheckResult("python_syntax", False, f"Invalid Python syntax in {path.relative_to(workspace_path)}: {exc.msg}")
        return CheckResult("python_syntax", True, "All generated Python files parse successfully")

    def _check_pyproject(self, request: MvpProjectRequest, workspace_path: Path) -> CheckResult:
        pyproject = workspace_path / "pyproject.toml"
        package_name = package_name_for_project(request.project_name)
        if not _PACKAGE_RE.fullmatch(package_name):
            return CheckResult("pyproject", False, f"Invalid package name: {package_name}")
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            return CheckResult("pyproject", False, f"Invalid pyproject.toml: {exc}")
        project = data.get("project")
        if not isinstance(project, dict):
            return CheckResult("pyproject", False, "pyproject.toml is missing [project]")
        if project.get("name") != request.project_name:
            return CheckResult("pyproject", False, "pyproject.toml project.name does not match request")
        if not (workspace_path / "src" / package_name).is_dir():
            return CheckResult("pyproject", False, f"Expected package directory is missing: src/{package_name}")
        return CheckResult("pyproject", True, "pyproject.toml and package layout are valid")
