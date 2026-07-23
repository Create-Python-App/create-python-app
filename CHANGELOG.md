# Changelog

## 0.2.11 - 2026-07-23

### CLI / argv trailing directory

- Do not treat `--template` / `-t` / other option *values* (e.g. `file://…`) as the project positional when expanding `--addons` / `--extend`. Fixes trailing `project_directory` being swallowed as an addon slug after a template URL (#245).

## 0.2.10 - 2026-07-22

### CLI / UX

- Validate non-empty target directory **before** the interactive wizard so a leftover default `my-project/` does not waste a full prompt session.
- Exit cleanly with a hint to use `--force` or pick a different directory name (no traceback).

## 0.2.9 - 2026-07-22

### CLI / argv trailing directory

- Stop treating a trailing `project_directory` after `--addons` / `--extend` as another addon value (e.g. `--addons a --addons b /tmp/app`).

## 0.2.8 - 2026-07-22

### CLI / argv

- Accept space-separated `--addons` / `--extend` values (CNA Commander parity): `--addons fastapi-docker github-setup` expands to repeated flags before Typer parses.

## 0.2.7 - 2026-07-22

### CLI

- Allow options after the project directory (`uvx create-awesome-python-app my-api --template …`). Typer was registering `cache` as a nested command group, so Click treated `--template` as a COMMAND name.

## 0.2.6 - 2026-07-18

### Docs

- Overhaul `create-awesome-python-app` README to Create-Node-App package parity (install channels, recipes, CLI/cache reference, site links).
- Refresh monorepo README as contributor-facing docs with a clear pointer to the package README.

## 0.2.5 - 2026-07-18

### Git cache

- Git cache refresh now advances HEAD to the remote default tip when `?ref=` is unset (CNA pull parity)
- Force-refresh when a configured template/extension `subdir` is missing from a warm cache (fixes post-rename `ManifestLoadError` for `all-github-setup` and friends)

## 0.2.4 - 2026-07-18

### Prompt rendering

- Template select titles use FormattedText styles (no more literal `^[[1;94m` ANSI escapes)

## 0.2.3 - 2026-07-18

### Discovery UX

- Template picker is now a browsable select with type-to-filter (↑↓ + search)
- High-contrast CPA blue/green prompt theme and bright category badges

## 0.2.2 - 2026-07-17

### Interactive CLI

- Template autocomplete no longer embeds ANSI category badges (questionary HTML parse error while typing to search)

## 0.2.1 - 2026-07-17

### Fixes

- Interactive template autocomplete no longer passes unsupported `pointer` to prompt_toolkit (`TypeError: PromptSession.__init__() got an unexpected keyword argument 'pointer'`)

## 0.2.0 - 2026-07-17

### Highlights

- Catalog slugs resolve to registry URLs (`--template fastapi-starter` works end-to-end)
- Release prep automation (`prepare_release.py` + `Prepare release PR` workflow)
- Hardened distribution smoke (PyPI/`uvx`, Docker, Homebrew, AUR) with clearer version checks
- AUR publish preflight + post-publish verification
- Cross-platform scaffold smoke (Ubuntu / macOS / Windows) against published `uvx`

### CLI / core

- Resolve `cpa-templates` catalog slugs for `--template` / `--addons` before cloning
- `--list-templates` / `--list-addons` reflect the live catalog (including new starters)

### Tooling

- Changelog-driven GitHub Release notes via `extract_release_notes.py`
- Docs: `VERSIONING.md`, `DISTRIBUTION_SETUP.md`, cross-platform tracking

Paired catalog growth lives in [cpa-templates](https://github.com/Create-Python-App/cpa-templates) (`cli-starter`, `celery-worker`, `django-api`, `uv-workspace-starter`, extension pack, typed FastAPI default, CNA-parity `github-setup`).

## 0.1.0

First public release of:

- `create-python-app-core` — scaffolding engine (Jinja `.template` / `.append`, `pyproject.toml` merge, git cache, `file://` / GitHub sources)
- `create-awesome-python-app` — Typer CLI

Default template catalog: `Create-Python-App/cpa-templates` (`templates.json`).

### Install

```bash
uvx create-awesome-python-app@0.1.0 my-api --template fastapi-starter --no-interactive
```
