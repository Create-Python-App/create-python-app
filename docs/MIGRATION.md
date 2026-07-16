# Migration Guide

How to keep a scaffolded project aligned with improvements in
`create-awesome-python-app` and
[cpa-templates](https://github.com/Create-Python-App/cpa-templates).

## Why migration is hard

`create-awesome-python-app` generates a **one-time snapshot** of a template plus
extensions. After scaffolding, the CLI does not maintain a live link to your
project. You own every file and dependency choice going forward.

That is by design -- generated projects should be independent -- but it means
updates require deliberate effort.

## Strategy 1: Manual dependency updates

1. Run `uv lock --upgrade` (or `uv lock --upgrade-package <name>`) in your
   project to refresh pinned versions in `uv.lock`.
2. Enable Dependabot if you used the `github-setup` extension (see its workflow
   in cpa-templates).
3. Compare your `pyproject.toml` scripts, dependency groups, and dev tools
   with the current template in
   [cpa-templates](https://github.com/Create-Python-App/cpa-templates/tree/main/templates).

Use `uv tree --outdated` when available to spot stale direct dependencies.

## Strategy 2: Diff against a fresh scaffold

Scaffold a new project with the same template and extensions, then diff:

```bash
uvx create-awesome-python-app@latest my-project-new \
  -t <template-slug> \
  --addons <extension-slugs> \
  --no-install \
  --no-interactive

diff -r my-project/ my-project-new/ \
  --exclude=.venv \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=.pytest_cache \
  --exclude=.ruff_cache \
  --exclude=dist \
  --exclude=build
```

Review differences in config files (`pyproject.toml`, `ruff.toml`, CI
workflows, `.python-version`) and port changes selectively.

## Strategy 3: Selective re-scaffolding

For a single extension update:

1. Scaffold a throwaway project with only that extension applied.
2. Copy the extension-specific files into your existing project (e.g. Alembic
   migrations, auth middleware, GitHub Actions workflows).
3. Merge `pyproject.toml` dependency changes manually.

## CNA to CPA renames

If you are porting workflows, docs, or CI from
[create-node-app](https://github.com/Create-Node-App/create-node-app), use the
CPA equivalents:

| CNA | CPA |
|-----|-----|
| `cna.config.json` | `cpa.config.json` |
| `package.json` manifest | `pyproject.toml` |
| `CNA_CACHE_DIR` | `CPA_CACHE_DIR` |
| `CNA_REFRESH` | `CPA_REFRESH` |
| `CNA_REFRESH_AFTER_HOURS` | `CPA_REFRESH_AFTER_HOURS` |
| `CNA_NO_CATALOG_CACHE` | `CPA_NO_CATALOG_CACHE` |
| `CNA_CATALOG_URL` | `CPA_CATALOG_URL` |
| `CNA_STRICT_VERSION` | `CPA_STRICT_VERSION` |
| `CNA_STRICT_REPRO` | `CPA_STRICT_REPRO` |
| `CNA_SKIP_GIT` | `CPA_SKIP_GIT` |
| `CNA_USER_AGENT` | `CPA_USER_AGENT` |
| `~/.cache/cna` (default cache) | `~/.cache/cpa` (default cache) |

CLI flags are the same shape (`--template` / `-t`, `--addons`, `--cache-dir`,
`--refresh`, `--pin`, `--offline`, `--no-install`). See
[cpa-vs-cna-config.md](./cpa-vs-cna-config.md) for manifest and tooling
differences (npm vs `uv`, ESLint vs Ruff).

## Template URL format and slug resolution

The catalog lives in
[cpa-templates `templates.json`](https://github.com/Create-Python-App/cpa-templates/blob/main/templates.json).
Each entry has a `slug` and a `url`.

**Slug resolution.** Pass a slug instead of a full URL and the CLI resolves it
from the catalog:

```bash
create-awesome-python-app my-app -t fastapi-starter --addons github-setup
```

Run `--list-templates` or `--list-addons` to see available slugs. Invalid
slugs fail with a hint to pass a full URL.

**GitHub URLs with `?subdir=`.** Remote templates use the monorepo layout:

```text
https://github.com/Create-Python-App/cpa-templates?subdir=templates/fastapi-starter
https://github.com/Create-Python-App/cpa-templates?subdir=extensions/github-setup
```

**Local `file://` URLs.** For forks, air-gapped work, or integration tests:

```bash
create-awesome-python-app my-app \
  -t "file:///path/to/cpa-templates?subdir=templates/fastapi-starter" \
  --no-install
```

**Pinning a revision.** Append `?ref=<sha-or-tag>` to the URL, or use
`--pin <ref>` (equivalent to adding `ref=` to the template URL). With
`CPA_STRICT_REPRO=1`, `ref` must be a full 40-character commit SHA.

**Catalog override.** Point at a fork or fixture:

```bash
export CPA_CATALOG_URL="file:///path/to/templates.json"
export CPA_NO_CATALOG_CACHE=1   # skip on-disk catalog cache
```

See [templates-json-schema.md](./templates-json-schema.md) for the full catalog
shape.

## CLI version changelog

Track releases for template and extension changes:

- [create-python-app releases](https://github.com/Create-Python-App/create-python-app/releases)
- [cpa-templates releases](https://github.com/Create-Python-App/cpa-templates/releases)

When upgrading the CLI:

```bash
# ephemeral (recommended)
uvx create-awesome-python-app@latest --help

# Homebrew / AUR / pipx installs
brew upgrade create-awesome-python-app
pipx upgrade create-awesome-python-app
```

Use `--strict-version` (or `CPA_STRICT_VERSION=1`) in CI to fail when the
installed CLI is not the latest PyPI release.

Manage the template cache:

```bash
create-awesome-python-app cache dir
create-awesome-python-app cache list
create-awesome-python-app cache update [id]
create-awesome-python-app cache clean
```

## Adding extensions to an existing project

There is no `cpa add-extension` command yet. To add an extension after the fact:

1. Browse the extension in
   [cpa-templates/extensions](https://github.com/Create-Python-App/cpa-templates/tree/main/extensions).
2. Read the extension README for required files and dependencies.
3. Scaffold a minimal project with that extension and copy the relevant files.
4. Install matching dependencies from the extension's `pyproject.toml` (or run
   `uv sync` in the throwaway project and mirror the dependency blocks).

Use `--list-addons -t <template-slug>` to see extensions compatible with your
base template.

## Migrating from Cookiecutter or Copier

If you are moving a hand-rolled Cookiecutter/Copier flow into the CPA
ecosystem:

1. Map your template repo to a `templates.json` entry (slug, name, category,
   `url` with `?subdir=`).
2. Add `cpa.config.json` at the template root (see
   [cpa-config-schema.md](./cpa-config-schema.md)).
3. Prefer `uv` lockfiles (`uv.lock`) in generated projects instead of
   unpinned `requirements.txt` unless the template explicitly targets pip-only
   workflows.
4. Convert Jinja-style prompts to `customOptions` in `cpa.config.json` where
   possible; use `--set key=value` for non-interactive runs.

## Getting help

- [Troubleshooting](./TROUBLESHOOTING.md)
- [GitHub Issues](https://github.com/Create-Python-App/create-python-app/issues)
- [Discussions](https://github.com/Create-Python-App/create-python-app/discussions)
