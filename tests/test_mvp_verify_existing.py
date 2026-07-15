from pathlib import Path

from cli.main import main
from mvp.integrations.codex import FakeMvpCodexAdapter, package_name_for_project
from mvp.models import MvpProjectRequest
from mvp.workspace import WorkspaceManager


def _project(tmp_path: Path, name="task-tracker"):
    manager = WorkspaceManager(tmp_path / "root")
    ws = manager.create_workspace("generated")
    req = MvpProjectRequest("Create CLI", name, "cli", "owner/repo")
    FakeMvpCodexAdapter(manager).generate_project(req, ws)
    # convert fake custom backend to approved setuptools for strict verification
    (ws.path / "pyproject.toml").write_text(
        f'''[build-system]\nrequires = []\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "{name}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = []\n\n[project.optional-dependencies]\ntest = ["pytest>=8,<10"]\n\n[tool.setuptools.packages.find]\nwhere = ["src"]\n''',
        encoding="utf-8",
    )
    (ws.path / "slugger_mvp_backend.py").unlink(missing_ok=True)
    return ws.path, tmp_path / "root", name


def test_verify_existing_cli_succeeds(tmp_path: Path):
    project, root, name = _project(tmp_path)
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 0
    )
    assert (project / "verification-evidence.json").exists()


def test_verify_existing_invalid_path_returns_nonzero(tmp_path: Path):
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(tmp_path / "missing"),
                "--project-name",
                "bad-path",
                "--workspace-root",
                str(tmp_path / "root"),
            ]
        )
        == 1
    )


def test_verify_existing_validation_install_test_smoke_failures(tmp_path: Path):
    project, root, name = _project(tmp_path / "v")
    (project / "README.md").unlink()
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 1
    )
    project, root, name = _project(tmp_path / "i")
    (project / "pyproject.toml").write_text(
        "[build-system]\nbuild-backend='bad'\nrequires=[]\n"
    )
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 1
    )
    project, root, name = _project(tmp_path / "t")
    (project / "tests" / "test_main.py").write_text("def test_bad(): assert False\n")
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 1
    )
    project, root, name = _project(tmp_path / "s")
    pkg = package_name_for_project(name)
    (project / "src" / pkg / "main.py").write_text(
        "def main(): return 0\nif __name__ == '__main__': raise SystemExit(main())\n"
    )
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 1
    )


def test_verify_existing_rejects_unsafe_packaging_and_paths(tmp_path: Path):
    for rel, content in [(".github/workflows/x.yml", "x"), (".git/config", "x")]:
        project, root, name = _project(tmp_path / rel.replace("/", "_"))
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        assert (
            main(
                [
                    "mvp",
                    "verify-existing",
                    "--project-dir",
                    str(project),
                    "--project-name",
                    name,
                    "--workspace-root",
                    str(root),
                ]
            )
            == 1
        )
    project, root, name = _project(tmp_path / "dep")
    txt = (
        (project / "pyproject.toml")
        .read_text()
        .replace("dependencies = []", 'dependencies = ["evil @ file:///tmp/evil"]')
    )
    (project / "pyproject.toml").write_text(txt)
    assert (
        main(
            [
                "mvp",
                "verify-existing",
                "--project-dir",
                str(project),
                "--project-name",
                name,
                "--workspace-root",
                str(root),
            ]
        )
        == 1
    )
