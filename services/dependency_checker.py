"""Dependency update checker — identify outdated project dependencies.

:class:`DependencyChecker` compares declared dependency versions against
the latest versions available on PyPI (or a custom registry) and reports
which packages need updating.

For environments without network access the checker accepts a pre-populated
version map so it can be used in tests without hitting external services.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DependencyStatus:
    """Status of a single declared dependency.

    Parameters
    ----------
    name:
        Package name.
    declared_version:
        Version string as declared in the manifest or requirements file.
    latest_version:
        Latest available version, or ``None`` if lookup failed.
    up_to_date:
        Whether *declared_version* matches *latest_version*.
    error:
        Optional error message if the lookup failed.
    """

    name: str
    declared_version: str
    latest_version: str | None = None
    up_to_date: bool = False
    error: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'declared_version': self.declared_version,
            'latest_version': self.latest_version,
            'up_to_date': self.up_to_date,
            'error': self.error,
        }


class DependencyChecker:
    """Check declared dependencies for available updates.

    Parameters
    ----------
    version_map:
        Pre-populated ``{package_name: latest_version}`` mapping.  When
        ``None`` the checker fetches from PyPI.  Provide this in tests or
        air-gapped environments.
    timeout:
        HTTP request timeout in seconds.

    Examples
    --------
    >>> checker = DependencyChecker(version_map={'requests': '2.32.0'})
    >>> checker.check({'requests': '2.31.0'})
    [DependencyStatus(name='requests', declared_version='2.31.0', latest_version='2.32.0', up_to_date=False)]
    """

    PYPI_URL = 'https://pypi.org/pypi/{package}/json'

    def __init__(
        self,
        version_map: dict[str, str] | None = None,
        timeout: float = 5.0,
    ) -> None:
        self._version_map = version_map  # None means use network
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, dependencies: dict[str, str]) -> list[DependencyStatus]:
        """Check *dependencies* for updates.

        Parameters
        ----------
        dependencies:
            Mapping of ``{package_name: declared_version}``.

        Returns
        -------
        list[DependencyStatus]
            One entry per package.
        """
        results: list[DependencyStatus] = []
        for name, declared_version in dependencies.items():
            latest, error = self._latest_version(name)
            up_to_date = latest == declared_version if latest else False
            results.append(
                DependencyStatus(
                    name=name,
                    declared_version=declared_version,
                    latest_version=latest,
                    up_to_date=up_to_date,
                    error=error,
                )
            )
        return results

    def outdated(self, dependencies: dict[str, str]) -> list[DependencyStatus]:
        """Return only the packages that are **not** up to date."""
        return [s for s in self.check(dependencies) if not s.up_to_date and not s.error]

    def summary(self, dependencies: dict[str, str]) -> dict[str, Any]:
        """Return a summary dict including counts and per-package details."""
        statuses = self.check(dependencies)
        up_to_date = [s for s in statuses if s.up_to_date]
        outdated = [s for s in statuses if not s.up_to_date and not s.error]
        errors = [s for s in statuses if s.error]
        return {
            'total': len(statuses),
            'up_to_date': len(up_to_date),
            'outdated': len(outdated),
            'errors': len(errors),
            'packages': [s.to_dict() for s in statuses],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _latest_version(self, name: str) -> tuple[str | None, str]:
        """Return ``(latest_version, error_message)``."""
        if self._version_map is not None:
            latest = self._version_map.get(name)
            if latest is None:
                return None, f"Package '{name}' not found in version map."
            return latest, ''
        # Network lookup
        url = self.PYPI_URL.format(package=name)
        try:
            with urllib.request.urlopen(url, timeout=self._timeout) as resp:  # noqa: S310
                data = json.loads(resp.read())
            return data['info']['version'], ''
        except Exception as exc:  # noqa: BLE001
            return None, str(exc)
