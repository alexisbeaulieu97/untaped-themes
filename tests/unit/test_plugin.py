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
from typer.testing import CliRunner
from untaped import UiContext, get_settings
from untaped.main import build_app
from untaped.plugins import PluginRegistry
from untaped.settings import reset_config_registry_for_tests

from untaped_themes.plugin import THEMES, plugin

REPO_ROOT = Path(__file__).resolve().parents[2]
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


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
    assert plugin.untaped_api_version == 1


def test_theme_plugin_registers_exactly_three_themes() -> None:
    registry = PluginRegistry()

    plugin.register(registry)

    assert set(registry.themes) == {"classic", "high-contrast", "quiet"}
    assert registry.themes == THEMES


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

    result = CliRunner().invoke(
        app,
        ["config", "list", "--format", "table", "--columns", "key", "--columns", "value"],
    )

    assert result.exit_code == 0, result.output
    assert "key: log_level" in result.stdout
    assert "value: INFO" in result.stdout
    assert "┏" not in result.stdout
