# Changelog

## 0.2.5 - 2026-07-18

### Fixes

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
