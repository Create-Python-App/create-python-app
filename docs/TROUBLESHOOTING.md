# Troubleshooting

Common issues when scaffolding projects with `create-awesome-python-app`.

## Python version mismatch

**Symptoms:** The CLI exits immediately with a Python version error.

**Requirement:** Python **>= 3.12**

```bash
python --version
```

**Switch versions:**

- [uv](https://docs.astral.sh/uv/): `uv python install 3.12 && uv python pin 3.12`
- [pyenv](https://github.com/pyenv/pyenv): `pyenv install 3.12 && pyenv local 3.12`
- [mise](https://mise.jdx.dev/): `mise use python@3.12`

The workspace pin file is `.python-version` (currently `3.12`). Generated projects
inherit `requires-python` from their template.

## Non-empty target directory

**Symptoms:** Scaffolding aborts with `CPA_NON_EMPTY_TARGET_DIR` or
`Target directory is not empty: <path>`.

**Cause:** CPA refuses to scaffold into a directory that already contains files,
to avoid overwriting user data.

**Fix:**

```bash
# Scaffold into a new directory (default: my-project)
uvx create-awesome-python-app my-new-app -t fastapi-starter --no-interactive

# Or allow scaffolding into a non-empty directory
uvx create-awesome-python-app existing-dir -t fastapi-starter --force --no-interactive
```

Use `--force` / `-f` only when you intend to merge into an existing tree.

## Catalog and slug errors

**Symptoms:** `Invalid catalog slug: '<slug>'. Run --list-templates / --list-addons or pass a full URL.`

**Cause:** The `-t`, `--addons`, or `--extend` value does not match any entry in
`templates.json` from [cpa-templates](https://github.com/Create-Python-App/cpa-templates).

**Fix:**

```bash
# List official templates
uvx create-awesome-python-app --list-templates

# List extensions (optionally filtered by template)
uvx create-awesome-python-app --list-addons -t fastapi-starter

# Use the exact slug from the catalog
uvx create-awesome-python-app my-app -t fastapi-starter --no-interactive
```

**Tips:**

- Slugs are case-sensitive (`fastapi-starter`, not `FastAPI-Starter`).
- Pass a full URL when using a fork or local template instead of a catalog slug.
- Override the catalog source for forks or offline testing:

```bash
CPA_CATALOG_URL="file:///path/to/cpa-templates/templates.json" \
  uvx create-awesome-python-app my-app -t fastapi-starter --no-interactive
```

If the catalog fetch fails but a disk cache exists, CPA falls back to the cached
copy and prints a yellow warning. With no cache and no fixture, scaffolding fails
with `Failed to load template catalog`.

## Template URL not found

**Symptoms:** Scaffolding fails with HTTP 404, `repository not found`, or
`file source not found` (`CPA_FILE`).

**Tips:**

- Registry templates use slugs: `uvx create-awesome-python-app my-app -t fastapi-starter`
- Custom URLs must be valid GitHub HTTPS URLs, `git@` SSH targets, or `file://` paths
- Pin a branch, tag, or commit with `?ref=`:

```bash
uvx create-awesome-python-app my-app \
  -t "https://github.com/Create-Python-App/cpa-templates?subdir=templates/fastapi-starter&ref=main"
```

- Test a local template checkout:

```bash
uvx create-awesome-python-app my-app \
  -t "file:///path/to/cpa-templates?subdir=templates/fastapi-starter"
```

- List official templates: `uvx create-awesome-python-app --list-templates`

For reproducible CI builds, pin a full 40-character commit SHA and set
`CPA_STRICT_REPRO=1` so non-SHA `ref` values are rejected.

## Cache location and inspection

By default, CPA caches the template catalog and git repos under `~/.cache/cpa`.
The CLI exposes this via:

```bash
uvx create-awesome-python-app cache dir       # print the cache root
uvx create-awesome-python-app cache list      # entries: id, url, ref, last fetched, sha, size
uvx create-awesome-python-app cache verify    # run git fsck on every entry
uvx create-awesome-python-app cache verify <id>  # verify one entry
uvx create-awesome-python-app cache clean     # remove all repo entries
uvx create-awesome-python-app cache clean <id>   # remove one entry by id
uvx create-awesome-python-app cache clean --catalog  # also clear catalog/templates.json cache
uvx create-awesome-python-app cache outdated    # compare local SHAs to remote tips
uvx create-awesome-python-app cache update      # refresh all cached repos
uvx create-awesome-python-app cache update <id> # refresh one entry
uvx create-awesome-python-app cache doctor      # check git, network, cache dir, integrity
```

Layout:

```text
~/.cache/cpa/
  catalog/
    templates.json
  repos/
    <cache-key>/
      .cpa-cache.json
      ...
```

If a scaffold "looks weird" and you suspect a stale cache, the first diagnostic
step is `cache verify`. If any entry fails, `cache clean` and re-run. Use
`cache outdated` + `cache update` when you need newer template content without
a full re-download.

## Forcing a fresh fetch

```bash
# Force a re-fetch of templates.json and template repos on every run.
uvx create-awesome-python-app my-app -t fastapi-starter --no-cache --no-interactive

# Disable git pull on cache hit (use the local copy as-is).
uvx create-awesome-python-app my-app -t fastapi-starter --offline --no-interactive

# Control refresh policy explicitly (default: stale).
uvx create-awesome-python-app my-app -t fastapi-starter --refresh always --no-interactive
uvx create-awesome-python-app my-app -t fastapi-starter --refresh manual --no-interactive

# Pin the cache to a project-local directory (useful in CI).
CPA_CACHE_DIR="$PWD/.cpa-cache" uvx create-awesome-python-app my-app -t fastapi-starter --no-interactive

# Or use the CLI flag (sets CPA_CACHE_DIR internally)
uvx create-awesome-python-app my-app -t fastapi-starter --cache-dir "$PWD/.cpa-cache" --no-interactive
```

### CPA_* environment variables

| Variable | Purpose |
|----------|---------|
| `CPA_CACHE_DIR` | Override cache root (default `~/.cache/cpa`) |
| `CPA_CATALOG_URL` | Override catalog URL (default raw GitHub `templates.json`) |
| `CPA_NO_CATALOG_CACHE` | Set by `--no-cache`; skip in-memory/disk catalog cache |
| `CPA_REFRESH` | Refresh mode: `always`, `stale` (default), or `manual` |
| `CPA_REFRESH_AFTER_HOURS` | Hours before a stale entry is refreshed (default `24`) |
| `CPA_STRICT_REPRO` | Require full 40-char SHA in `?ref=` for reproducibility |
| `CPA_STRICT_VERSION` | Fail when CLI is older than latest PyPI release |
| `CPA_SKIP_GIT` | Skip `git init` in generated project (testing) |
| `CPA_CATALOG_FIXTURE` | Load bundled catalog fixture (testing) |
| `CPA_TEMPLATES_ROOT` | Local `cpa-templates` checkout for integration tests |

`--no-cache` sets `CPA_NO_CATALOG_CACHE=1` and forces `--refresh always` for
template repos. `--offline` uses cached repos only; a cache miss raises
`CPA_OFFLINE`.

See also: [MIGRATION.md](./MIGRATION.md) for keeping scaffolded projects up to date.

## uv sync failures

**Symptoms:** Scaffolding copies files but fails during `uv sync` in the generated
project, or exits with `CPA_ABORTED`.

**Cause:** The template includes a `pyproject.toml` and CPA runs `uv sync` by
default to install dependencies.

**Fix:**

1. Confirm `uv` is installed and on `PATH`:

```bash
uv --version
create-awesome-python-app --info
```

1. Check the generated project's `.python-version` and `requires-python` in
    `pyproject.toml` match your interpreter.

1. Retry manually inside the project:

```bash
cd my-app
uv sync
```

1. If you only need the file tree (no install), skip sync during scaffold:

```bash
uvx create-awesome-python-app my-app -t fastapi-starter --no-install --no-interactive
```

1. For network or index issues, retry with verbose logging or behind a proxy;
    CPA does not wrap `uv` output -- read the `uv sync` error directly.

## Git clone failures

**Symptoms:** `git clone failed` (`CPA_GIT`), `git executable not found`, or
`offline mode: cache miss` (`CPA_OFFLINE`).

**Cause:** CPA clones template and extension repos from GitHub (or custom URLs)
into the local cache before copying layers.

**Fix:**

1. Confirm git is available:

```bash
git --version
create-awesome-python-app --info
```

1. Warm the cache while online, then scaffold offline:

```bash
uvx create-awesome-python-app my-app -t fastapi-starter --no-interactive
uvx create-awesome-python-app my-app2 -t fastapi-starter --offline --no-interactive
```

1. For private repos, ensure SSH keys or credentials work outside CPA:

```bash
git ls-remote git@github.com:your-org/your-template.git
```

1. Clear a corrupted cache entry and retry:

```bash
uvx create-awesome-python-app cache verify
uvx create-awesome-python-app cache clean
uvx create-awesome-python-app my-app -t fastapi-starter --no-interactive
```

1. Use `file://` URLs to scaffold from a local checkout without network access.

## incompatibleWith errors

**Symptoms:** `Incompatible extension combination from cpa.config.json: 'foo' <-> 'bar'. Remove one of each conflicting pair and retry.`

**Cause:** Two or more selected extensions declare each other in `incompatibleWith`
(either in `cpa.config.json` or in catalog metadata). CPA validates addon/extend
layers before merging.

**Fix:**

1. List extensions and read their descriptions:

```bash
uvx create-awesome-python-app --list-addons -t fastapi-starter
```

1. Remove one extension from each conflicting pair in `--addons` / `--extend`.

1. When authoring extensions, set `incompatibleWith` in `cpa.config.json`:

```json
{
  "name": "postgres",
  "incompatibleWith": ["sqlite"]
}
```

Matches use each layer's `name` field (slug-like id), not the catalog display name.

## `--set` values with spaces

When passing custom options that contain spaces, quote the entire `key=value` pair:

```bash
uvx create-awesome-python-app my-app -t fastapi-starter \
  --set 'projectName=My Awesome Project' \
  --no-interactive
```

Multiple `--set` flags merge into the Jinja context alongside `cpa.config.json`
defaults.

## CI reproduction tips

Reproduce scaffold failures locally the way CI does:

```bash
# Match the test workflow environment
git clone https://github.com/Create-Python-App/create-python-app.git
cd create-python-app
git clone https://github.com/Create-Python-App/cpa-templates.git ../cpa-templates

uv sync --group dev
export CPA_TEMPLATES_ROOT="$(cd ../cpa-templates && pwd)"
export CPA_SKIP_GIT=1
export CPA_CACHE_DIR="$PWD/.cpa-cache-ci"
export CPA_NO_CATALOG_CACHE=1

uv run create-awesome-python-app test-app \
  -t fastapi-starter \
  --no-interactive \
  --cache-dir "$CPA_CACHE_DIR"
```

**Checklist:**

- Use `--no-interactive` in CI (interactive prompts are skipped when `CI=true`).
- Pin `CPA_CACHE_DIR` to a workspace path for cache reuse across steps.
- Set `CPA_CATALOG_URL` to a `file://` catalog when testing forks offline.
- Run `create-awesome-python-app --info` in bug reports (Python, uv, git versions).
- Run `create-awesome-python-app cache doctor` before blaming template content.
- Use `CPA_STRICT_REPRO=1` and a full commit SHA in `?ref=` for deterministic builds.

## Distribution channels

Install the CLI from PyPI or run it ephemerally with uv:

```bash
# Ephemeral (recommended for end users)
uvx create-awesome-python-app@latest my-app

# Pin a release
uvx create-awesome-python-app@0.1.0 my-app --template fastapi-starter --no-interactive

# Install into the active environment
uv tool install create-awesome-python-app
create-awesome-python-app my-app -t fastapi-starter --no-interactive
```

Other channels (same package, different installers):

| Channel | Install |
|---------|---------|
| **PyPI** | `uv tool install create-awesome-python-app` or `uvx create-awesome-python-app` |
| **Homebrew** | `brew tap Create-Python-App/tap && brew install create-awesome-python-app` |
| **AUR** | `yay -S create-awesome-python-app` |
| **Docker** | `docker run --rm -v "${PWD}:/app" -w /app ulisesjeremias/create-awesome-python-app my-app` |

Verify the installed version:

```bash
create-awesome-python-app --version
uvx create-awesome-python-app@latest --version
```

If behavior differs between `uvx` and a global install, compare versions and
clear the uv tool cache. See [DISTRIBUTION_SETUP.md](./DISTRIBUTION_SETUP.md) for
maintainer release workflow.
