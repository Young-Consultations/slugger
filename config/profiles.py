"""Configuration profiles — multi-environment settings management.

:class:`ProfileManager` loads environment-specific configuration profiles
(development, staging, production, …) and merges them with a base settings
object, allowing the same codebase to run correctly in multiple environments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from config.settings import Settings
from config.loader import ConfigLoader


@dataclass
class Profile:
    """A named configuration profile.

    Parameters
    ----------
    name:
        Profile name (e.g. ``'production'``).
    overrides:
        Key-value pairs that override the base configuration when this profile
        is active.  Keys use dot-notation (e.g. ``'observability.log_level'``).
    extends:
        Optional parent profile name.  If set, this profile's overrides are
        layered on top of the parent's.
    description:
        Human-readable description of when this profile should be used.
    """

    name: str
    overrides: dict[str, Any] = field(default_factory=dict)
    extends: str | None = None
    description: str = ''

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            'name': self.name,
            'overrides': self.overrides,
            'description': self.description,
        }
        if self.extends:
            result['extends'] = self.extends
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Profile':
        return cls(
            name=data['name'],
            overrides=data.get('overrides', {}),
            extends=data.get('extends'),
            description=data.get('description', ''),
        )


class ProfileManager:
    """Manage and activate configuration profiles.

    Parameters
    ----------
    root_path:
        Repository root directory (used to locate ``config/`` files).
    profiles_path:
        Optional path to a YAML file containing profile definitions.  If not
        provided defaults to ``{root_path}/config/profiles.yaml``.

    Examples
    --------
    >>> manager = ProfileManager(Path('.'))
    >>> manager.register(Profile('ci', overrides={'observability.log_level': 'WARNING'}))
    >>> settings = manager.activate('ci', base_settings)
    """

    def __init__(
        self,
        root_path: Path,
        profiles_path: Path | None = None,
    ) -> None:
        self._root = root_path
        self._loader = ConfigLoader(root_path)
        self._profiles: dict[str, Profile] = {}
        self._active: str | None = None

        path = profiles_path or (root_path / 'config' / 'profiles.yaml')
        if path.exists():
            self._load_file(path)

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def register(self, profile: Profile) -> None:
        """Register a profile.  Replaces any existing profile with the same name."""
        self._profiles[profile.name] = profile

    def get(self, name: str) -> Profile | None:
        """Return the profile named *name*, or ``None``."""
        return self._profiles.get(name)

    @property
    def available(self) -> list[str]:
        """Names of all registered profiles."""
        return list(self._profiles.keys())

    @property
    def active_profile(self) -> str | None:
        """Name of the currently active profile, or ``None``."""
        return self._active

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def activate(self, name: str, base: Settings | None = None) -> Settings:
        """Apply the profile named *name* on top of *base* settings.

        The profile's ``overrides`` dict uses dot-notation keys to update
        nested settings fields.

        Parameters
        ----------
        name:
            Profile to activate.
        base:
            Base :class:`~config.settings.Settings` object.  If ``None`` a
            default-constructed settings object is used.

        Returns
        -------
        Settings
            A new :class:`Settings` instance with the profile's overrides applied.

        Raises
        ------
        KeyError
            If the profile is not registered.
        """
        profile = self._profiles.get(name)
        if profile is None:
            raise KeyError(f"Profile '{name}' is not registered.")

        # Collect overrides from parent chain
        overrides = self._resolve_overrides(profile)

        settings = base if base is not None else Settings()
        self._apply_overrides(settings, overrides)
        self._active = name
        return settings

    # ------------------------------------------------------------------
    # File persistence
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        """Write all profiles to a YAML *path*."""
        data = [p.to_dict() for p in self._profiles.values()]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: Path) -> None:
        raw = yaml.safe_load(path.read_text(encoding='utf-8')) or []
        for item in raw:
            if isinstance(item, dict):
                self.register(Profile.from_dict(item))

    def _resolve_overrides(self, profile: Profile) -> dict[str, Any]:
        """Merge parent and child overrides (child wins)."""
        if profile.extends:
            parent = self._profiles.get(profile.extends)
            if parent:
                base_overrides = self._resolve_overrides(parent)
                return {**base_overrides, **profile.overrides}
        return dict(profile.overrides)

    def _apply_overrides(self, settings: Settings, overrides: dict[str, Any]) -> None:
        """Apply dot-notation overrides to *settings* in place."""
        for key, value in overrides.items():
            parts = key.split('.')
            obj: Any = settings
            for part in parts[:-1]:
                obj = getattr(obj, part, None)
                if obj is None:
                    break
            if obj is not None and hasattr(obj, parts[-1]):
                setattr(obj, parts[-1], value)
            elif len(parts) == 1 and hasattr(settings, parts[0]):
                setattr(settings, parts[0], value)
