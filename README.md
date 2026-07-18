<!--lint disable double-link awesome-heading awesome-git-repo-age awesome-toc-->

<div align="center">

# Create Awesome Python App

**The open-source monorepo behind `create-awesome-python-app`: compose templates and addons into production-ready Python, FastAPI, Django, Celery, CLI, and uv workspace projects.**

One command. Any stack.

[![CI Tests](https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml)
[![Lint](https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml)
[![Typecheck](https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml)
[![PyPI](https://img.shields.io/pypi/v/create-awesome-python-app.svg)](https://pypi.org/project/create-awesome-python-app/)
[![Docker](https://img.shields.io/docker/v/ulisesjeremias/create-awesome-python-app?style=flat-square&label=Docker&logo=docker&color=2496ED)](https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app)
[![AUR](https://img.shields.io/aur/version/create-awesome-python-app?label=AUR&logo=archlinux)](https://aur.archlinux.org/packages/create-awesome-python-app)
[![Homebrew](https://img.shields.io/badge/homebrew-Create--Python--App%2Ftap-orange?logo=homebrew)](https://github.com/Create-Python-App/homebrew-tap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[Package README](./packages/create-awesome-python-app/README.md) · [Official Site](https://create-awesome-python-app.vercel.app) · [Templates](https://create-awesome-python-app.vercel.app/templates) · [Extensions](https://create-awesome-python-app.vercel.app/extensions) · [Contributing](./CONTRIBUTING.md) · [Troubleshooting](./docs/TROUBLESHOOTING.md)

</div>

---

## What This Repo Contains

This repository contains the source code for [`create-awesome-python-app`](https://pypi.org/project/create-awesome-python-app/), the CLI that composes curated templates, addons, custom options, and AI-ready conventions into working projects.

Use this README if you want to understand the codebase, run it locally, contribute a fix, improve documentation, or work on the CLI packages. If you only want to generate an app, start with the [package README](./packages/create-awesome-python-app/README.md).

---

## Quick Start For Users

```bash
uvx create-awesome-python-app@latest my-app
```

Run headlessly for scripts, CI, or platform automation:

```bash
uvx create-awesome-python-app my-api \
  --template fastapi-starter \
  --addons github-setup \
  --addons fastapi-sqlalchemy \
  --no-interactive
```

More examples live in the [CLI package README](./packages/create-awesome-python-app/README.md).

---

## Ecosystem

| Repository | Role |
|------------|------|
| [create-python-app](https://github.com/Create-Python-App/create-python-app) (this repo) | CLI (`create-awesome-python-app`) and scaffolding engine (`create-python-app-core`) |
| [cpa-templates](https://github.com/Create-Python-App/cpa-templates) | Official templates and extensions (`templates.json` catalog) |
| [website](https://github.com/Create-Python-App/website) | Docs + catalog UI ([create-awesome-python-app.vercel.app](https://create-awesome-python-app.vercel.app)) |
| [homebrew-tap](https://github.com/Create-Python-App/homebrew-tap) | Homebrew formula |
| [aur-package](https://github.com/Create-Python-App/aur-package) | AUR PKGBUILD mirror |

The CLI fetches the catalog from:

`https://raw.githubusercontent.com/Create-Python-App/cpa-templates/main/templates.json`

Override with `CPA_CATALOG_URL` for forks or local testing (`file://` supported).

---

## Repository Map

This is a **virtual uv workspace**: the root is not published; packages live under `packages/*` and share one `uv.lock` / `.venv`.

| Path | Purpose |
|------|---------|
| [`packages/create-awesome-python-app`](./packages/create-awesome-python-app) | Main CLI package (Typer), interactive wizard, catalog listing |
| [`packages/create-python-app-core`](./packages/create-python-app-core) | Scaffolding engine: resolve sources, merge layers, install, git init |
| [`docs/`](./docs) | Brand, troubleshooting, migration, distribution, versioning |
| [`.github/workflows`](./.github/workflows) | CI, release, Docker / Homebrew / AUR publish, distribution smoke |

Template and extension data is maintained in [`Create-Python-App/cpa-templates`](https://github.com/Create-Python-App/cpa-templates). This repo consumes that catalog remotely.

```text
create-python-app/          # virtual workspace root (no [project] table)
├── pyproject.toml          # [tool.uv.workspace] members = ["packages/*"]
├── uv.lock
├── .venv/
└── packages/
    ├── create-python-app-core/       # scaffolding engine
    └── create-awesome-python-app/    # CLI (depends on core via workspace)
```

---

## Local Development

Requires **Python 3.12+** (pinned in `.python-version`) and [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/Create-Python-App/create-python-app.git
cd create-python-app
uv sync --group dev
uv run create-awesome-python-app --help
```

Non-interactive local smoke test:

```bash
uv run create-awesome-python-app smoke-app \
  --template fastapi-starter \
  --addons github-setup \
  --no-interactive \
  --no-install
```

Install git hooks: `uv run pre-commit install`

---

## Development Commands

| Task | Make | Equivalent |
|------|------|------------|
| Install workspace | `make sync` | `uv sync --group dev` |
| Tests | `make test` | `uv run pytest` |
| Lint | `make lint` | `uv run ruff check .` |
| Type-check | `make typecheck` | `uv run pyright` |
| Build packages | `make build` | `uv build --all` |

---

## Install Channels (published package)

```bash
# PyPI / uv
uvx create-awesome-python-app@latest my-app

# Homebrew
brew tap Create-Python-App/tap
brew install create-awesome-python-app

# AUR
yay -S create-awesome-python-app

# Docker
docker run --rm -it -v "${PWD}:/app" -w /app \
  ulisesjeremias/create-awesome-python-app:latest my-app \
  --template fastapi-starter
```

Published image: [`ulisesjeremias/create-awesome-python-app`](https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app)

Local image build (installs the given PyPI version into the image):

```bash
docker build --build-arg VERSION=0.2.5 -t create-awesome-python-app .
docker run --rm create-awesome-python-app --help
```

---

## License

MIT — see [LICENSE](./LICENSE).

### Reference

- [Package README](./packages/create-awesome-python-app/README.md) — user-facing CLI docs
- [uv workspaces handbook](https://pydevtools.com/handbook/how-to/how-to-set-up-a-python-monorepo-with-uv-workspaces/)
- [cpa-templates](https://github.com/Create-Python-App/cpa-templates) — template and extension bank
- Node parity: [Create-Node-App/create-node-app](https://github.com/Create-Node-App/create-node-app) + [cna-templates](https://github.com/Create-Node-App/cna-templates)
