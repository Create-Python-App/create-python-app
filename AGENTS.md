# Agent Instructions for create-python-app

## Overview

`create-python-app` is a CLI tool for scaffolding Python projects from templates
(parity with [Create-Node-App/create-node-app](https://github.com/Create-Node-App/create-node-app)).

Roadmap: [#1](https://github.com/Create-Python-App/create-python-app/issues/1).

## Tech Stack

- Python 3.12+ (see `.python-version`)
- [uv](https://docs.astral.sh/uv/) workspaces (virtual root + `packages/*`)
- Typer (CLI — Epic 4)
- Ruff (lint/format — Epic 2)
- Pyright (types — Epic 2)
- pytest (tests — Epic 2)

## Packages

| Package | Role |
|---------|------|
| `create-python-app-core` | Scaffolding engine |
| `create-awesome-python-app` | User-facing CLI (`uvx` / console script) |

## Key Commands

```bash
uv sync
make test        # uv run pytest
make lint        # uv run ruff check .
make typecheck   # uv run pyright
make build       # uv build --all
uv run create-awesome-python-app --help
```

## Code Style

- Ruff for lint + format
- Pyright for type checking
- Prefer minimal, issue-linked changes; English for commits/PRs
