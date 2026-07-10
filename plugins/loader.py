"""Plugin discovery loader."""

from __future__ import annotations

import importlib.util
from pathlib import Path


class PluginLoader:
    """Discovers plugin modules from configured directories."""

    def discover(self, directories: list[str]) -> list[Path]:
        candidates: list[Path] = []
        for directory in directories:
            path = Path(directory)
            if not path.exists():
                continue
            candidates.extend(sorted(path.rglob('*_plugin.py')))
        return candidates

    def load_module(self, path: Path) -> object:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f'Unable to load plugin module: {path}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
