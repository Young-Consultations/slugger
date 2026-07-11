"""Release automation — coordinate versioning, changelog, and GitHub release creation.

:class:`ReleaseAutomation` drives the release lifecycle:

1. Compute the next SemVer version from the current tag and bump type.
2. Update the version string in ``pyproject.toml``.
3. Generate a changelog section from recent Git commit messages.
4. Produce a release notes document.

It does **not** push to Git or call the GitHub API directly; those steps are
left to the CI environment so the class is fully testable without credentials.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------- #
# Version helpers                                                              #
# --------------------------------------------------------------------------- #

_SEMVER_RE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)(?:-.+)?$')


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a SemVer string into ``(major, minor, patch)`` integers.

    Raises
    ------
    ValueError
        If *version* does not match the expected pattern.
    """
    match = _SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"Cannot parse version string: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(version: str, bump: str) -> str:
    """Return the next SemVer string after a *bump*.

    Parameters
    ----------
    version:
        Current version (e.g. ``'1.2.3'`` or ``'v1.2.3'``).
    bump:
        One of ``'major'``, ``'minor'``, or ``'patch'``.

    Returns
    -------
    str
        New version string (without leading ``v``).
    """
    major, minor, patch = parse_version(version)
    if bump == 'major':
        return f'{major + 1}.0.0'
    if bump == 'minor':
        return f'{major}.{minor + 1}.0'
    if bump == 'patch':
        return f'{major}.{minor}.{patch + 1}'
    raise ValueError(f"Unknown bump type: {bump!r}  — expected 'major', 'minor', or 'patch'.")


# --------------------------------------------------------------------------- #
# Models                                                                       #
# --------------------------------------------------------------------------- #

@dataclass
class CommitSummary:
    """A single commit line for changelog purposes."""

    sha: str
    message: str
    author: str = ''


@dataclass
class ReleaseNotes:
    """Generated release notes for a version.

    Parameters
    ----------
    version:
        The version being released (e.g. ``'1.3.0'``).
    previous_version:
        The version being superseded.
    commits:
        Commit summaries included in the release.
    notes:
        Final rendered Markdown release notes.
    """

    version: str
    previous_version: str
    commits: list[CommitSummary] = field(default_factory=list)
    notes: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'version': self.version,
            'previous_version': self.previous_version,
            'commit_count': len(self.commits),
            'notes': self.notes,
        }


# --------------------------------------------------------------------------- #
# Automation class                                                             #
# --------------------------------------------------------------------------- #

class ReleaseAutomation:
    """Orchestrate the release process for the Slugger project.

    Parameters
    ----------
    repo_root:
        Root directory of the Git repository.
    pyproject_path:
        Path to ``pyproject.toml``.  Defaults to ``{repo_root}/pyproject.toml``.
    """

    def __init__(self, repo_root: Path, pyproject_path: Path | None = None) -> None:
        self.repo_root = repo_root
        self.pyproject_path = pyproject_path or (repo_root / 'pyproject.toml')

    # ------------------------------------------------------------------
    # Version management
    # ------------------------------------------------------------------

    def current_version(self) -> str:
        """Return the version string currently in ``pyproject.toml``."""
        text = self.pyproject_path.read_text(encoding='utf-8')
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
        if not match:
            raise ValueError(f"Cannot find 'version' in {self.pyproject_path}")
        return match.group(1)

    def update_version(self, new_version: str) -> str:
        """Rewrite the version string in ``pyproject.toml``.

        Returns the previous version.
        """
        text = self.pyproject_path.read_text(encoding='utf-8')
        previous = self.current_version()
        updated = re.sub(
            r'^(version\s*=\s*["\'])[^"\']+(["\'])',
            rf'\g<1>{new_version}\g<2>',
            text,
            flags=re.MULTILINE,
        )
        self.pyproject_path.write_text(updated, encoding='utf-8')
        return previous

    # ------------------------------------------------------------------
    # Changelog helpers
    # ------------------------------------------------------------------

    def recent_commits(self, since_tag: str | None = None, max_count: int = 50) -> list[CommitSummary]:
        """Return recent Git commits as :class:`CommitSummary` objects.

        Parameters
        ----------
        since_tag:
            If provided, only commits after this tag are returned.
        max_count:
            Maximum number of commits.
        """
        cmd = ['git', '-C', str(self.repo_root), 'log',
               '--pretty=format:%H|%s|%an', f'-{max_count}']
        if since_tag:
            cmd.append(f'{since_tag}..HEAD')
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            summaries: list[CommitSummary] = []
            for line in result.stdout.splitlines():
                parts = line.split('|', 2)
                if len(parts) == 3:
                    summaries.append(CommitSummary(sha=parts[0][:8], message=parts[1], author=parts[2]))
            return summaries
        except subprocess.CalledProcessError:
            return []

    # ------------------------------------------------------------------
    # Release notes
    # ------------------------------------------------------------------

    def generate_release_notes(
        self,
        new_version: str,
        previous_version: str | None = None,
        since_tag: str | None = None,
    ) -> ReleaseNotes:
        """Generate structured release notes.

        Parameters
        ----------
        new_version:
            The version being released.
        previous_version:
            The previous version string (for display purposes).
        since_tag:
            Git tag marking the start of the range.

        Returns
        -------
        ReleaseNotes
        """
        previous = previous_version or self.current_version()
        commits = self.recent_commits(since_tag=since_tag)

        lines = [
            f'## {new_version}',
            '',
            '### Changes',
            '',
        ]
        if commits:
            for c in commits:
                lines.append(f'- {c.message} ({c.sha})')
        else:
            lines.append('_No commits found since the previous release._')

        notes = '\n'.join(lines) + '\n'
        return ReleaseNotes(
            version=new_version,
            previous_version=previous,
            commits=commits,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # Full release workflow
    # ------------------------------------------------------------------

    def prepare_release(self, bump: str = 'patch') -> ReleaseNotes:
        """Compute the next version, update pyproject.toml, and generate notes.

        Parameters
        ----------
        bump:
            Version component to increment: ``'major'``, ``'minor'``, or ``'patch'``.

        Returns
        -------
        ReleaseNotes
            Ready-to-publish release notes.
        """
        current = self.current_version()
        new_version = bump_version(current, bump)
        self.update_version(new_version)
        return self.generate_release_notes(new_version, previous_version=current)
