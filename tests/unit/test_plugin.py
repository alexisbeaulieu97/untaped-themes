"""Tests for the untaped themes plugin."""

from __future__ import annotations

import io
import json
import os
import re
import tomllib
from collections.abc import Iterator
from pathlib import Path

import pytest
from untaped import UiContext, get_settings
from untaped.api import PluginManifest
from untaped.main import build_app
from untaped.plugins import PluginRegistry, register_plugins
from untaped.settings import reset_config_registry_for_tests
from untaped.testing import CliInvoker

from untaped_themes.plugin import THEMES, plugin

REPO_ROOT = Path(__file__).resolve().parents[2]
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
EXPECTED_SYMBOLS = {
    "success": "",
    "warning": "",
    "error": "",
    "info": "",
}
EXPECTED_THEME_CONTRACTS = {
    "high-contrast": {
        "border": "square",
        "density": "normal",
        "collection_view": "table",
        "detail_view": "list",
        "color_roles": {
            "header": "bold bright_cyan",
            "border": "bright_cyan",
            "key": "bold bright_cyan",
            "value": "bright_white",
            "success": "bold bright_green",
            "info": "bold bright_blue",
            "warning": "bold yellow",
            "error": "bold bright_red",
        },
    },
    "quiet": {
        "border": "none",
        "density": "compact",
        "collection_view": "list",
        "detail_view": "list",
        "color_roles": {
            "key": "dim cyan",
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        },
    },
    "classic": {
        "border": "rounded",
        "density": "normal",
        "collection_view": "table",
        "detail_view": "list",
        "color_roles": {
            "header": "bold cyan",
            "border": "cyan",
            "key": "cyan",
            "value": "white",
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        },
    },
}


class TtyStringIO(io.StringIO):
    """StringIO that advertises TTY support to Rich."""

    def isatty(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    cfg = tmp_path / "config.yml"
    monkeypatch.setenv("UNTAPED_CONFIG", str(cfg))
    monkeypatch.delenv("UNTAPED_PROFILE", raising=False)
    reset_config_registry_for_tests()
    get_settings.cache_clear()
    yield cfg
    os.environ.pop("UNTAPED_PROFILE", None)
    reset_config_registry_for_tests()
    get_settings.cache_clear()


def _has_ansi(value: str) -> bool:
    return bool(ANSI_RE.search(value))


def test_theme_plugin_entry_point_is_declared() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())

    assert data["project"]["entry-points"]["untaped.plugins"]["themes"] == (
        "untaped_themes.plugin:plugin"
    )


def test_theme_plugin_declares_contract() -> None:
    assert plugin.id == "themes"
    assert plugin.untaped_api_version == 3


def test_manifest_contributes_exactly_three_themes_and_nothing_else() -> None:
    manifest = plugin.manifest()

    assert isinstance(manifest, PluginManifest)
    assert set(manifest.themes) == {"classic", "high-contrast", "quiet"}
    assert manifest.themes == THEMES
    assert not manifest.clis
    assert not manifest.profile_settings
    assert not manifest.state_settings
    assert not manifest.skills
    assert not manifest.diagnostics


def test_core_registers_manifest_without_load_errors() -> None:
    registry = PluginRegistry()

    register_plugins(registry, [plugin])

    assert registry.load_errors == []
    assert registry.plugin_ids == {"themes"}
    assert registry.themes == THEMES


@pytest.mark.parametrize("name", ["classic", "high-contrast", "quiet"])
def test_registered_theme_presets_match_v1_contract(name: str) -> None:
    theme = plugin.manifest().themes[name]
    expected = EXPECTED_THEME_CONTRACTS[name]
    assert theme.border == expected["border"]
    assert theme.density == expected["density"]
    assert theme.collection_view == expected["collection_view"]
    assert theme.detail_view == expected["detail_view"]
    assert theme.color_roles == expected["color_roles"]
    assert theme.symbols == EXPECTED_SYMBOLS


def test_human_theme_output_emits_ansi_for_tty_stdout() -> None:
    ui = UiContext(theme=THEMES["high-contrast"], stdout=TtyStringIO())

    output = ui.collection(
        [{"name": "default", "status": "ok"}],
        fmt="table",
        columns=["name", "status"],
    )

    assert _has_ansi(output)
    assert "default" in output


@pytest.mark.parametrize("fmt", ["json", "yaml", "raw"])
def test_structured_output_stays_ansi_free_for_tty_stdout(fmt: str) -> None:
    ui = UiContext(theme=THEMES["high-contrast"], stdout=TtyStringIO())

    output = ui.collection(
        [{"name": "default", "status": "ok"}],
        fmt=fmt,  # type: ignore[arg-type]
        columns=["name", "status"],
    )

    assert not _has_ansi(output)
    assert "default" in output
    if fmt == "json":
        assert json.loads(output) == [{"name": "default", "status": "ok"}]


def test_root_app_uses_plugin_theme_for_human_table_output(_isolate_config: Path) -> None:
    _isolate_config.write_text("ui:\n  theme: quiet\nprofiles:\n  default:\n    log_level: INFO\n")
    app = build_app(plugins=[plugin])

    result = CliInvoker().invoke(
        app,
        ["config", "list", "--format", "table", "--columns", "key", "--columns", "value"],
    )

    assert result.exit_code == 0, result.output
    assert "key: log_level" in result.stdout
    assert "value: INFO" in result.stdout
    assert "┏" not in result.stdout
