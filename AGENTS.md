# AGENTS.md - `untaped-themes`

Single source of truth for this standalone plugin repo. If theme behavior,
plugin contract behavior, or workflow changes, update this file in the same
commit.

## Mission

`untaped-themes` is an `untaped` plugin. It owns external terminal theme
presets registered through core `ThemeSpec`. `untaped` core owns the binary,
plugin discovery, UI rendering, config/profile resolution, and structured
output behavior.

## Hard Rules

1. Keep `AGENTS.md` up to date.
2. Expose the plugin through the `untaped.plugins` entry point. The plugin
   object must expose `id = "themes"`, literal `untaped_api_version = 2`, and
   `register(registry)`.
3. This plugin registers theme presets only. Do not add a Cyclopts app, settings
   model, diagnostics, renderer API, prompt primitives, or agent skill in v1.
4. Theme presets use `untaped.ThemeSpec`; do not duplicate renderer logic.
5. Theme names are unprefixed and must remain unique: `high-contrast`,
   `quiet`, and `classic`.
6. Do not set message symbols unless the product direction explicitly changes;
   v1 preserves existing message wording and uses color roles for semantics.
7. Structured formats must stay plain. Tests must cover that `json`, `yaml`,
   and `raw` emit no ANSI even when the active theme has color roles.
8. Finish with `uv --cache-dir .uv-cache run ruff check`,
   `uv --cache-dir .uv-cache run ruff format --check`,
   `uv --cache-dir .uv-cache run mypy`, and
   `uv --cache-dir .uv-cache run pytest`.

## Architecture

```text
src/untaped_themes/
├── __init__.py
└── plugin.py
```

The plugin object registers three `ThemeSpec` presets with
`registry.add_theme(...)`. It does not mount any CLI commands. Core resolves
the selected theme from the global `ui.theme` setting and keeps structured
formats independent from theme styling.
