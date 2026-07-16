# create-python-app

[![CI Tests](https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/test.yml)
[![Lint](https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/lint.yml)
[![Typecheck](https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml/badge.svg)](https://github.com/Create-Python-App/create-python-app/actions/workflows/type-check.yml)
[![PyPI](https://img.shields.io/pypi/v/create-awesome-python-app.svg)](https://pypi.org/project/create-awesome-python-app/)
[![Docker](https://img.shields.io/docker/v/ulisesjeremias/create-awesome-python-app?style=flat-square&label=Docker&logo=docker&color=2496ED)](https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app)
[![AUR](https://img.shields.io/aur/version/create-awesome-python-app?label=AUR&logo=archlinux)](https://aur.archlinux.org/packages/create-awesome-python-app)
[![Homebrew](https://img.shields.io/badge/homebrew-Create--Python--App%2Ftap-orange?logo=homebrew)](https://github.com/Create-Python-App/homebrew-tap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Composable scaffolding CLI for production-ready Python apps.

> **Status:** CLI monorepo bootstrapped. Template bank: [`cpa-templates`](https://github.com/Create-Python-App/cpa-templates). Roadmap: [#1](https://github.com/Create-Python-App/create-python-app/issues/1).

## Ecosystem

| Repository | Role |
|------------|------|
| [create-python-app](https://github.com/Create-Python-App/create-python-app) (this repo) | CLI (`create-awesome-python-app`) and scaffolding engine (`create-python-app-core`) |
| [cpa-templates](https://github.com/Create-Python-App/cpa-templates) | Official templates and extensions (`templates.json` catalog) |
| [homebrew-tap](https://github.com/Create-Python-App/homebrew-tap) | Homebrew formula |
| [aur-package](https://github.com/Create-Python-App/aur-package) | AUR PKGBUILD mirror |

The CLI fetches the catalog from:

`https://raw.githubusercontent.com/Create-Python-App/cpa-templates/main/templates.json`

Override with `CPA_CATALOG_URL` for forks or local testing (`file://` supported).

## Install

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
  ulisesjeremias/create-awesome-python-app my-app
```

Or pin a version:

```bash
uvx create-awesome-python-app@0.1.0 my-app --template fastapi-starter --no-interactive
```

From this workspace (development):

```bash
uv sync
uv run create-awesome-python-app --help
```

### Shell completion

```bash
create-awesome-python-app --install-completion   # bash / zsh / fish
create-awesome-python-app --show-completion      # print script only
```

## License

MIT — see [LICENSE](./LICENSE).

## Monorepo layout (uv workspaces)

This repository is a **virtual uv workspace**: the root is not published; packages live under `packages/*` and share one `uv.lock` / `.venv`.

```text
create-python-app/          # virtual workspace root (no [project] table)
├── pyproject.toml          # [tool.uv.workspace] members = ["packages/*"]
├── uv.lock
├── .venv/
└── packages/
    ├── create-python-app-core/       # scaffolding engine
    └── create-awesome-python-app/    # CLI (depends on core via workspace)
```

### Setup

```bash
# Requires uv: https://docs.astral.sh/uv/
uv sync --group dev
```

## Development commands

From the repo root (requires [uv](https://docs.astral.sh/uv/)):

| Task | Make | Equivalent |
|------|------|------------|
| Install workspace | `make sync` | `uv sync --group dev` |
| Tests | `make test` | `uv run pytest` |
| Lint | `make lint` | `uv run ruff check .` |
| Type-check | `make typecheck` | `uv run pyright` |
| Build packages | `make build` | `uv build --all` |

Install git hooks: `uv run pre-commit install`

## Python version

- **Pin file:** `.python-version` → `3.12`
- **Constraint:** every workspace member sets `requires-python = ">=3.12"`
- **CI:** workflows install Python 3.12+ matching this pin

```bash
uv python install
uv sync --group dev
```

## Docker

Published image: [`ulisesjeremias/create-awesome-python-app`](https://hub.docker.com/r/ulisesjeremias/create-awesome-python-app)

```bash
docker run --rm ulisesjeremias/create-awesome-python-app:0.1.0 --version
docker run --rm -it -v "${PWD}:/app" -w /app \
  ulisesjeremias/create-awesome-python-app my-app --template fastapi-starter --no-interactive
```

Local build (installs the given PyPI version into the image):

```bash
docker build --build-arg VERSION=0.1.0 -t create-awesome-python-app .
docker run --rm create-awesome-python-app --help
```

### Reference

- [uv workspaces handbook](https://pydevtools.com/handbook/how-to/how-to-set-up-a-python-monorepo-with-uv-workspaces/)
- [cpa-templates](https://github.com/Create-Python-App/cpa-templates) — template and extension bank
- Node parity: [Create-Node-App/create-node-app](https://github.com/Create-Node-App/create-node-app) + [cna-templates](https://github.com/Create-Node-App/cna-templates)
