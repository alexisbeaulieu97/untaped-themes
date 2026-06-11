"""Untaped plugin registration for terminal theme presets."""

from __future__ import annotations

from untaped.api import PluginManifest, ThemeSpec

THEMES: dict[str, ThemeSpec] = {
    "high-contrast": ThemeSpec(
        border="square",
        density="normal",
        collection_view="table",
        detail_view="list",
        color_roles={
            "header": "bold bright_cyan",
            "border": "bright_cyan",
            "key": "bold bright_cyan",
            "value": "bright_white",
            "success": "bold bright_green",
            "info": "bold bright_blue",
            "warning": "bold yellow",
            "error": "bold bright_red",
        },
    ),
    "quiet": ThemeSpec(
        border="none",
        density="compact",
        collection_view="list",
        detail_view="list",
        color_roles={
            "key": "dim cyan",
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        },
    ),
    "classic": ThemeSpec(
        border="rounded",
        density="normal",
        collection_view="table",
        detail_view="list",
        color_roles={
            "header": "bold cyan",
            "border": "cyan",
            "key": "cyan",
            "value": "white",
            "success": "green",
            "info": "blue",
            "warning": "yellow",
            "error": "red",
        },
    ),
}


class ThemesPlugin:
    """Contribute packaged terminal theme presets to the untaped runtime."""

    id = "themes"
    untaped_api_version = 3

    def manifest(self) -> PluginManifest:
        return PluginManifest(themes=THEMES)


plugin = ThemesPlugin()
