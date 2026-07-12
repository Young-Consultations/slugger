"""Tests for TASK-059: Plugin SDK."""

from __future__ import annotations


from plugins.base import BasePlugin
from plugins.metadata import PluginMetadata
from plugins.sdk import PluginManifest, PluginSDK


class _FakePlugin(BasePlugin):
    def __init__(self, name: str = "fake-plugin") -> None:
        super().__init__(PluginMetadata(name=name, version="1.0.0", description="Fake"))

    def load(self) -> None:
        self.loaded = True

    def unload(self) -> None:
        self.loaded = False

    def health_check(self) -> bool:
        return True


def test_create_manifest() -> None:
    sdk = PluginSDK()
    manifest = sdk.create_manifest("my-plugin", "2.0.0", "My plugin")
    assert manifest.name == "my-plugin"
    assert manifest.version == "2.0.0"
    assert manifest.description == "My plugin"


def test_validate_valid_manifest() -> None:
    sdk = PluginSDK()
    manifest = sdk.create_manifest("my-plugin", "1.0.0", "A plugin")
    report = sdk.validate(manifest)
    assert report.valid
    assert report.errors == []


def test_validate_empty_name_error() -> None:
    sdk = PluginSDK()
    manifest = PluginManifest(name="", version="1.0.0")
    report = sdk.validate(manifest)
    assert not report.valid
    assert any("name" in e for e in report.errors)


def test_validate_invalid_name_characters() -> None:
    sdk = PluginSDK()
    manifest = PluginManifest(name="My Plugin!", version="1.0.0")
    report = sdk.validate(manifest)
    assert not report.valid


def test_validate_empty_version_error() -> None:
    sdk = PluginSDK()
    manifest = PluginManifest(name="valid-name", version="")
    report = sdk.validate(manifest)
    assert not report.valid
    assert any("version" in e for e in report.errors)


def test_validate_missing_main_warning() -> None:
    sdk = PluginSDK()
    manifest = PluginManifest(name="my-plugin", version="1.0.0", capabilities=["run"])
    report = sdk.validate(manifest)
    assert report.valid  # warnings don't fail
    assert any("main" in w for w in report.warnings)


def test_register_plugin() -> None:
    sdk = PluginSDK()
    plugin = _FakePlugin("fake-plugin")
    sdk.register_plugin(plugin)
    assert "fake-plugin" in sdk.registry.list()


def test_manifest_to_plugin_metadata() -> None:
    manifest = PluginManifest(
        name="cool-plugin",
        version="3.0.0",
        description="Cool",
        main="cool.Plugin",
        capabilities=["gen"],
    )
    meta = manifest.to_plugin_metadata()
    assert meta.name == "cool-plugin"
    assert meta.entry_point == "cool.Plugin"


def test_manifest_round_trip_dict() -> None:
    manifest = PluginManifest(
        name="abc-plugin",
        version="1.0.0",
        author="Alice",
        license="Apache-2.0",
        capabilities=["x"],
    )
    data = manifest.to_dict()
    restored = PluginManifest.from_dict(data)
    assert restored.name == manifest.name
    assert restored.author == manifest.author
    assert restored.license == manifest.license
