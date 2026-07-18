<!--lint disable double-link awesome-heading awesome-git-repo-age awesome-toc-->

<div align="center">

<img src="https://raw.githubusercontent.com/Create-Python-App/create-python-app/main/packages/create-awesome-python-app/assets/hero.svg" alt="Create Awesome Python App banner" width="100%" />

# Create Awesome Python App

**One command. Any stack.** Generate production-ready Python apps by composing templates, addons, and AI-ready conventions.

From blank folder to a working FastAPI, Django, Celery, CLI, or uv workspace project with modern tooling and team-friendly automation.

[![PyPI][pypiversion]][pypiurl]
[![Python][pythonbadge]][pythonurl]
[![Stars][starsbadge]][starsurl]
[![License: MIT][licensebadge]][licenseurl]

[![AUR][aurbadge]][aururl]
[![Homebrew][homebrewbadge]][homebrewurl]
[![Docker][dockerbadge]][dockerurl]
[![Smoke tests][smokebadge]][smokeurl]

[![Tests][testsbadge]][testsurl]
[![Lint][lintbadge]][linturl]
[![Typecheck][typecheckbadge]][typecheckurl]
[![MegaLinter][megalinterbadge]][megalinterurl]
[![Shellcheck][shellcheckbadge]][shellcheckurl]
[![Commit Activity][commitactivitybadge]][commitactivityurl]

**[Official Site](https://create-awesome-python-app.vercel.app)** · [Templates](https://create-awesome-python-app.vercel.app/templates) · [Extensions](https://create-awesome-python-app.vercel.app/extensions) · [Docs](https://create-awesome-python-app.vercel.app/docs) · [GitHub](https://github.com/Create-Python-App/create-python-app) · [PyPI](https://pypi.org/project/create-awesome-python-app/)

</div>

---

## Install

**uv (recommended):**

```bash
uvx create-awesome-python-app@latest my-app
```

**pipx:**

```bash
pipx run create-awesome-python-app my-app
```

**Homebrew (macOS / Linux):**

```bash
brew tap Create-Python-App/tap
brew install create-awesome-python-app
```

**AUR (Arch Linux):**

```bash
yay -S create-awesome-python-app   # or: paru -S create-awesome-python-app
```

**Docker:**

```bash
docker run --rm -it -v "${PWD}:/app" -w /app \
  ulisesjeremias/create-awesome-python-app:latest my-app \
  --template fastapi-starter
```

Interactive by default outside CI. For automation, run headless with flags:

```bash
uvx create-awesome-python-app my-api \
  --template fastapi-starter \
  --addons github-setup \
  --addons fastapi-sqlalchemy \
  --no-interactive
```

| If you want...                | Start here                                              |
| ----------------------------- | ------------------------------------------------------- |
| A guided local setup          | `uvx create-awesome-python-app@latest my-app`           |
| A repeatable CI/platform flow | `--no-interactive` with explicit flags                  |
| Your company starter          | `--template <github-url>` or `--template file://`       |
| Private standards layered in  | `--extend <url>`                                        |

### Shell completion

```bash
create-awesome-python-app --install-completion   # bash / zsh / fish
create-awesome-python-app --show-completion      # print script only
```

After installing, restart the shell (or `source` your profile) and tab-complete
flags such as `--template`, `--addons`, and `cache` subcommands.

---

## Why CPA?

| Capability                       | Value                                                                                          |
| -------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Composable by design**         | Start with a template, then layer only the addons your project actually needs.                 |
| **Production-ready defaults**    | uv, Ruff, Pyright, tests, docs, and practical DX defaults out of the box.                      |
| **AI-ready from day one**        | Supported templates generate `AGENTS.md` so coding agents understand the project context.      |
| **CI and platform friendly**     | Use `--no-interactive`, `--set`, `--template <url>`, and `--extend <url>` for repeatable runs. |

---

## Composition Model

```text
template -> addons -> custom options -> install -> git init -> AI-ready project
```

You can mix catalog templates and addons with your own GitHub or `file://` sources.

---

## What You Can Generate

### Template Families

| Category | Example templates                                      |
| -------- | ------------------------------------------------------ |
| Backend  | `fastapi-starter`, `django-api`, `celery-worker`       |
| CLI      | `cli-starter`                                          |
| Monorepo | `uv-workspace-starter`                                 |

### Addon Families

| Category       | Examples                                                      |
| -------------- | ------------------------------------------------------------- |
| CI / tooling   | `github-setup`, `development-container`                       |
| Containers     | `fastapi-docker`, `django-docker`, `celery-docker`            |
| Database       | `postgres`, `fastapi-sqlalchemy`, `fastapi-redis`             |
| Observability  | `fastapi-sentry`                                              |
| Security       | `fastapi-auth-jwt`                                            |

Browse the live catalog on the [official site](https://create-awesome-python-app.vercel.app/templates) or in [`cpa-templates`](https://github.com/Create-Python-App/cpa-templates).

---

## Popular Recipes

### FastAPI + GitHub + SQLAlchemy

```bash
uvx create-awesome-python-app my-api \
  --template fastapi-starter \
  --addons github-setup \
  --addons fastapi-sqlalchemy \
  --no-interactive
```

### Django API + Postgres + Docker

```bash
uvx create-awesome-python-app my-django \
  --template django-api \
  --addons github-setup \
  --addons postgres \
  --addons django-docker \
  --no-interactive
```

### Celery worker + Redis-friendly stack

```bash
uvx create-awesome-python-app my-worker \
  --template celery-worker \
  --addons github-setup \
  --addons celery-docker \
  --no-interactive
```

### Typer / Click CLI starter

```bash
uvx create-awesome-python-app my-cli \
  --template cli-starter \
  --addons github-setup \
  --no-interactive
```

### uv workspace monorepo

```bash
uvx create-awesome-python-app my-workspace \
  --template uv-workspace-starter \
  --addons github-setup \
  --no-interactive
```

### Internal platform template (GitHub URL)

```bash
uvx create-awesome-python-app my-internal-app \
  --template "https://github.com/your-org/platform-starters?subdir=templates/internal-app" \
  --no-interactive
```

### Local template development (`file://`)

```bash
uvx create-awesome-python-app my-local-app \
  --template "file:///absolute/path/to/cpa-templates?subdir=templates/fastapi-starter" \
  --no-interactive
```

> `file://` template URLs should be absolute paths (for example `file:///Users/...` or `file:///home/...`).

### Layer a private extension

```bash
uvx create-awesome-python-app my-app \
  --template fastapi-starter \
  --addons github-setup \
  --extend "https://github.com/your-org/platform-starters?subdir=extensions/company-ci"
```

### Pass custom template values

```bash
uvx create-awesome-python-app my-app \
  --template fastapi-starter \
  --set "productName=Acme Cloud" \
  --set "author=Platform Team" \
  --no-interactive
```

---

## Built For Modern Teams

- Python 3.12+ runtime support.
- uv-first workflows (with pipx / Homebrew / AUR / Docker install paths).
- Interactive wizard for local workflows.
- `--no-interactive` mode for CI, scripts, and platform automation.
- GitHub URL and local `file://` template inputs.
- `--extend` support for private addon layering.
- `--set key=value` overrides for deterministic custom options.

---

## Explore The Catalog

Browse visually at **[create-awesome-python-app.vercel.app](https://create-awesome-python-app.vercel.app)** or discover from the terminal:

```bash
# List all available templates
uvx create-awesome-python-app --list-templates

# List addons (optionally filtered by template)
uvx create-awesome-python-app --template fastapi-starter --list-addons
```

Full catalog:

- **Templates:** [create-awesome-python-app.vercel.app/templates](https://create-awesome-python-app.vercel.app/templates)
- **Extensions:** [create-awesome-python-app.vercel.app/extensions](https://create-awesome-python-app.vercel.app/extensions)
- **Source data:** [`cpa-templates/templates.json`](https://github.com/Create-Python-App/cpa-templates/blob/main/templates.json)

Override the catalog URL with `CPA_CATALOG_URL` (HTTPS or `file://`) for forks and local testing.

---

## AI-Ready With `AGENTS.md`

Supported templates generate an `AGENTS.md` file so coding assistants understand project context before editing:

| Context                | Why it matters                                              |
| ---------------------- | ----------------------------------------------------------- |
| Project purpose        | Agents understand what the app is for before changing code. |
| Directory layout       | Suggestions align with the real structure.                  |
| Scripts and validation | Agents know how to lint, test, and verify changes.          |
| Team conventions       | Output follows naming and workflow expectations.            |

---

## Interactive Wizard

Run the CLI without flags and CPA guides you through:

| Step              | What you choose                                                         |
| ----------------- | ----------------------------------------------------------------------- |
| Project name      | Confirm or set the target directory                                     |
| Category          | Backend, CLI, Monorepo, or custom URL                                   |
| Template          | Pick from curated starters with descriptions and labels                 |
| Addons            | Multi-select compatible extensions grouped by purpose                   |
| Custom options    | Answer `cpa.config.json` / registry prompts when present                |
| Custom extensions | Layer extra URLs for internal standards                                 |

---

## Requirements

- **Python >= 3.12**
- [uv](https://docs.astral.sh/uv/) recommended (or pipx / Homebrew / AUR / Docker)
- `git` available on `PATH` (required to clone templates)

Recommended quick start:

```bash
uv python install 3.12
uvx create-awesome-python-app@latest my-app
```

---

## CLI Reference

```text
Usage: create-awesome-python-app [OPTIONS] [project_directory]
```

| Flag                         | Description                                           |
| ---------------------------- | ----------------------------------------------------- |
| `--interactive`              | Force interactive wizard (default outside CI)         |
| `--no-interactive`           | Disable wizard and use flags only                     |
| `-t, --template <slug\|url>` | Template slug from catalog or remote/local URL        |
| `--addons <slug\|url>`       | Addon slug or URL (repeat the flag for multiple)      |
| `--extend <url>`             | Extra extension URL layered on top (repeatable)       |
| `--set <key=value>`          | Set custom template options; quote values with spaces |
| `--no-install`               | Generate files without installing dependencies        |
| `-f, --force`                | Allow scaffolding into a non-empty target directory   |
| `--list-templates`           | Print all templates                                   |
| `--list-addons`              | Print addons, optionally filtered by `--template`     |
| `--offline`                  | Use the local cache only; do not refresh templates    |
| `--no-cache`                 | Disable the catalog cache; force a refresh each run   |
| `--cache-dir <path>`         | Override the cache root (default: `~/.cache/cpa`)     |
| `--refresh <mode>`           | When to refresh: `always` \| `stale` \| `manual`      |
| `--pin <ref>`                | Pin template to a specific commit SHA, tag, or branch |
| `--strict-version`           | Fail if a newer CLI version is available              |
| `--keep-on-failure`          | Keep partial output if scaffolding fails              |
| `-v, --verbose`              | Output resolved generation config as JSON             |
| `-i, --info`                 | Print Python, uv, git, and OS diagnostics             |
| `--version`                  | Print CLI version                                     |
| `--help`                     | Show help                                             |

### `cache` subcommand

```text
Usage: create-awesome-python-app cache [OPTIONS] COMMAND [ARGS]...

Commands:
  dir         Print the cache root directory
  list        List cached templates and extensions
  clean       Remove one or all entries
  verify      Run `git fsck` on one or all entries
  outdated    List cached entries that are behind their remote tip
  update      Refresh one or all cached entries from their remote
  doctor      Diagnose cache health (git, network, permissions)
```

Inspect and manage the on-disk cache:

```bash
# Where is my cache?
uvx create-awesome-python-app cache dir
# /home/<you>/.cache/cpa

# What's in it?
uvx create-awesome-python-app cache list

# Verify integrity
uvx create-awesome-python-app cache verify

# Clear everything
uvx create-awesome-python-app cache clean

# Check for outdated entries
uvx create-awesome-python-app cache outdated

# Refresh a specific entry (or all)
uvx create-awesome-python-app cache update

# Diagnose cache health
uvx create-awesome-python-app cache doctor
```

---

## Cache & Updates

CPA caches both the **template catalog** (`templates.json` from
`raw.githubusercontent.com`) and the **template git repos** themselves. The
cache lives at `~/.cache/cpa` by default; override with `--cache-dir
<path>` or `CPA_CACHE_DIR`.

| Path                    | Contents                           |
| ----------------------- | ---------------------------------- |
| `~/.cache/cpa/catalog/` | Cached `templates.json`            |
| `~/.cache/cpa/repos/`   | Shallow clones of templates / addons |

### Refresh modes (set with `--refresh <mode>` or `CPA_REFRESH=<mode>`)

- **`stale`** (default): pull only when the cache is older than
  `CPA_REFRESH_AFTER_HOURS` (default `24`). No network on a warm cache.
- **`always`**: pull on every run.
- **`manual`**: never pull unless `--refresh` is passed.

### Pinning templates

Pin a template to a specific commit SHA, tag, or branch:

```bash
uvx create-awesome-python-app my-app \
  --template fastapi-starter \
  --pin abc123def456abc123def456abc123def456abc1 \
  --no-interactive
```

The `--pin` flag is equivalent to appending `?ref=<ref>` to the template URL.
Combine with `CPA_STRICT_REPRO=1` to enforce full 40-character SHAs.

### CI and offline usage

```bash
# Fully offline CI: use the local cache only, no network.
uvx create-awesome-python-app my-app \
  --template fastapi-starter \
  --offline \
  --no-interactive

# Pin the cache to a project-local directory (useful in monorepos and CI).
CPA_CACHE_DIR="$PWD/.cpa-cache" uvx create-awesome-python-app my-app \
  --template fastapi-starter \
  --no-interactive
```

---

## Programmatic Usage

Need to integrate CPA into your own tooling? The core is importable:

```python
import asyncio
from create_python_app_core import create_python_app

asyncio.run(
    create_python_app(
        "my-app",
        {
            "template": (
                "https://github.com/Create-Python-App/cpa-templates"
                "?subdir=templates/fastapi-starter"
            ),
            "addons": [],
            "install": False,
        },
    )
)
```

> The programmatic API is experimental and subject to change. Prefer the CLI for stable usage.

See also: [`create-python-app-core` README](https://github.com/Create-Python-App/create-python-app/blob/main/packages/create-python-app-core/README.md).

---

## Security

CPA downloads templates from remote sources. Prefer catalog slugs or hash-pinned
refs (`--pin` / `?ref=`), audit custom URLs before use, and report vulnerabilities
via GitHub Security Advisories on
[Create-Python-App/create-python-app](https://github.com/Create-Python-App/create-python-app).

---

## FAQ

<details>
<summary><strong>Why another scaffolder?</strong></summary>

Most scaffolders lock you into one stack. CPA is composable: choose a template, layer focused addons, and plug in your own GitHub/local blueprints — mirroring [Create Awesome Node App](https://github.com/Create-Node-App/create-node-app) for the Python ecosystem.

</details>

<details>
<summary><strong>Can I use my own template?</strong></summary>

Yes. Pass a GitHub URL or local `file://` URL with `--template` (supports `?subdir=` and `?ref=`).

</details>

<details>
<summary><strong>Can I use private/internal extensions?</strong></summary>

Yes. Use `--extend <url>` to layer private extensions on top of a template and addon set.

</details>

<details>
<summary><strong>Are addons order-sensitive?</strong></summary>

Yes. Addons are applied in sequence. If two addons modify the same file, later addons win.

</details>

<details>
<summary><strong>Does it support monorepos?</strong></summary>

Yes. Use `uv-workspace-starter` to bootstrap a multi-package uv workspace with shared tooling.

</details>

<details>
<summary><strong>Can I use it in CI?</strong></summary>

Yes. Pass all required flags and use `--no-interactive` for deterministic automation. Set `CI=true` to disable the wizard by default.

</details>

<details>
<summary><strong>Is Python 3.12 required?</strong></summary>

Yes. CPA targets Python 3.12+ to keep runtime behavior modern and predictable.

</details>

<details>
<summary><strong>Does CPA work with AI coding assistants?</strong></summary>

Yes. Supported templates generate `AGENTS.md`, helping assistants understand project layout, scripts, and conventions.

</details>

<details>
<summary><strong>Docker says `git executable not found`</strong></summary>

Images from `0.2.5` onward ship `git`. Pull `ulisesjeremias/create-awesome-python-app:latest` (or `0.2.5+`) and retry.

</details>

---

## Roadmap

- More framework templates and vertical starters.
- Additional testing and observability packs.
- Diff-based upgrade paths for pinned templates.
- Richer template analytics and usage insights.

Track progress in [Issues](https://github.com/Create-Python-App/create-python-app/issues) and [Discussions](https://github.com/Create-Python-App/create-python-app/discussions).

---

## Contributing

Templates, addons, bug fixes, docs, recipes, and ideas are all welcome.

- **Main repo:** [github.com/Create-Python-App/create-python-app](https://github.com/Create-Python-App/create-python-app)
- **Template and extension data:** [github.com/Create-Python-App/cpa-templates](https://github.com/Create-Python-App/cpa-templates)
- **Contributing guide:** [CONTRIBUTING.md](https://github.com/Create-Python-App/create-python-app/blob/main/CONTRIBUTING.md)
- **Troubleshooting:** [docs/TROUBLESHOOTING.md](https://github.com/Create-Python-App/create-python-app/blob/main/docs/TROUBLESHOOTING.md)

---

## License

MIT © [Create Python App Contributors](https://github.com/Create-Python-App/create-python-app/graphs/contributors)

---

<div align="center">

**[create-awesome-python-app.vercel.app](https://create-awesome-python-app.vercel.app)**

_Built for developers who value speed, composability, craft, and AI-ready workflows._

</div>

<!-- Reference links -->

[testsbadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml/badge.svg
[lintbadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml/badge.svg
[typecheckbadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml/badge.svg
[shellcheckbadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/shellcheck.yml/badge.svg
[megalinterbadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/mega-linter.yml/badge.svg
[pypiversion]: https://img.shields.io/pypi/v/create-awesome-python-app.svg?style=flat-square&color=3775A9
[pythonbadge]: https://img.shields.io/pypi/pyversions/create-awesome-python-app.svg?style=flat-square
[starsbadge]: https://img.shields.io/github/stars/Create-Python-App/create-python-app?style=flat-square&color=yellow
[licensebadge]: https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square
[testsurl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml
[linturl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml
[typecheckurl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml
[shellcheckurl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/shellcheck.yml
[megalinterurl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/mega-linter.yml
[pypiurl]: https://pypi.org/project/create-awesome-python-app/
[pythonurl]: https://pypi.org/project/create-awesome-python-app/
[licenseurl]: https://github.com/Create-Python-App/create-python-app/blob/main/LICENSE
[starsurl]: https://github.com/Create-Python-App/create-python-app/stargazers
[commitactivitybadge]: https://img.shields.io/github/commit-activity/m/Create-Python-App/create-python-app?style=flat-square&logo=github&label=commits
[commitactivityurl]: https://github.com/Create-Python-App/create-python-app/pulse
[aururl]: https://aur.archlinux.org/packages/create-awesome-python-app
[aurbadge]: https://img.shields.io/aur/version/create-awesome-python-app?style=flat-square&label=AUR&logo=archlinux
[homebrewurl]: https://github.com/Create-Python-App/homebrew-tap
[homebrewbadge]: https://img.shields.io/badge/homebrew-Create--Python--App%2Ftap-orange?style=flat-square&logo=homebrew
[dockerurl]: https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app
[dockerbadge]: https://img.shields.io/docker/v/ulisesjeremias/create-awesome-python-app?style=flat-square&label=Docker&logo=docker&color=2496ED
[smokebadge]: https://github.com/Create-Python-App/create-python-app/actions/workflows/smoke-distribution.yml/badge.svg?event=schedule
[smokeurl]: https://github.com/Create-Python-App/create-python-app/actions/workflows/smoke-distribution.yml
