"""Marketplace packaging — bundle a Slugger plugin for distribution.

:class:`MarketplacePackager` takes a plugin directory and produces a
self-contained archive (``*.slugger-plugin`` zip file) suitable for
uploading to a plugin registry or distributing directly.

The archive layout::

    <name>-<version>.slugger-plugin  (ZIP)
    ├── plugin.yaml                  ← serialised PluginManifest
    ├── README.md                    ← optional
    └── <plugin source files>        ← copied verbatim
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from plugins.sdk import PluginManifest


@dataclass
class PackageResult:
    """Outcome of a packaging operation.

    Parameters
    ----------
    archive_path:
        Path to the created ``*.slugger-plugin`` archive.
    manifest:
        The manifest embedded in the package.
    included_files:
        List of paths (relative to the plugin root) that were included.
    size_bytes:
        Total archive size in bytes.
    """

    archive_path: Path
    manifest: PluginManifest
    included_files: list[str] = field(default_factory=list)
    size_bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            'archive_path': str(self.archive_path),
            'manifest': self.manifest.to_dict(),
            'included_files': self.included_files,
            'size_bytes': self.size_bytes,
        }


class MarketplacePackager:
    """Build a distributable plugin archive from a source directory.

    Parameters
    ----------
    output_dir:
        Directory where the produced archive is written.

    Examples
    --------
    >>> packager = MarketplacePackager(output_dir=Path('dist'))
    >>> result = packager.package(manifest, plugin_dir=Path('my_plugin'))
    >>> result.archive_path
    PosixPath('dist/my-plugin-1.0.0.slugger-plugin')
    """

    ARCHIVE_EXT = '.slugger-plugin'
    MANIFEST_FILENAME = 'plugin.yaml'

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def package(
        self,
        manifest: PluginManifest,
        plugin_dir: Path,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> PackageResult:
        """Create a plugin archive.

        Parameters
        ----------
        manifest:
            Plugin manifest to embed.
        plugin_dir:
            Source directory containing the plugin's files.
        include_patterns:
            Glob patterns for files to include (relative to *plugin_dir*).
            Defaults to ``['**/*']``.
        exclude_patterns:
            Glob patterns for files to exclude.  Defaults to
            ``['**/__pycache__/**', '**/*.pyc']``.

        Returns
        -------
        PackageResult
        """
        archive_name = f'{manifest.name}-{manifest.version}{self.ARCHIVE_EXT}'
        archive_path = self.output_dir / archive_name

        include_patterns = include_patterns or ['**/*']
        exclude_set = set(exclude_patterns or ['**/__pycache__/**', '**/*.pyc'])

        included_files: list[str] = []

        with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # Embed the manifest
            manifest_yaml = yaml.safe_dump(manifest.to_dict(), sort_keys=False)
            zf.writestr(self.MANIFEST_FILENAME, manifest_yaml)

            # Include source files
            for pattern in include_patterns:
                for file_path in sorted(plugin_dir.glob(pattern)):
                    if not file_path.is_file():
                        continue
                    rel = file_path.relative_to(plugin_dir)
                    rel_str = str(rel)

                    # Apply exclusions
                    excluded = any(file_path.match(ep) for ep in exclude_set)
                    if excluded:
                        continue

                    zf.write(file_path, rel_str)
                    included_files.append(rel_str)

        return PackageResult(
            archive_path=archive_path,
            manifest=manifest,
            included_files=included_files,
            size_bytes=archive_path.stat().st_size,
        )

    @staticmethod
    def inspect(archive_path: Path) -> PluginManifest:
        """Extract and return the manifest from an existing archive.

        Parameters
        ----------
        archive_path:
            Path to the ``*.slugger-plugin`` archive.

        Returns
        -------
        PluginManifest

        Raises
        ------
        KeyError
            If the archive does not contain a ``plugin.yaml`` file.
        """
        with zipfile.ZipFile(archive_path, 'r') as zf:
            manifest_data = yaml.safe_load(zf.read('plugin.yaml').decode('utf-8'))
        return PluginManifest.from_dict(manifest_data)
