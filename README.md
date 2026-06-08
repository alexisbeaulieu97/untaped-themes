# untaped-themes

`untaped-themes` is a theme preset plugin for `untaped`.

It contributes three terminal themes through the `untaped.plugins` entry
point. It does not add commands, settings, diagnostics, renderers, prompt
APIs, or agent skills.

## Install

Generic plugin install and sync workflow is documented in the core
[`untaped` plugin docs](https://github.com/alexisbeaulieu97/untaped/blob/main/docs/plugins.md).

Install the plugin from git:

```bash
untaped plugins add "untaped-themes @ git+https://github.com/alexisbeaulieu97/untaped-themes.git@v0.1.0" \
  --tool-spec "git+https://github.com/alexisbeaulieu97/untaped.git@v0.1.3"
```

For editable core development:

```bash
untaped plugins add /path/to/untaped-themes \
  --tool-spec /path/to/untaped \
  --editable-tool
```

## Themes

Select a theme from the global `ui` section:

```yaml
ui:
  theme: high-contrast
```

Available themes:

- `high-contrast` — square table borders with strong color roles for
  headers, borders, values, keys, and semantic messages.
- `quiet` — compact borderless list output with restrained key and message
  colors.
- `classic` — rounded tables with subtle header, border, value, and semantic
  colors.

Theme presets affect human terminal output only. `--format json`,
`--format yaml`, and `--format raw` remain plain and pipe-friendly.
