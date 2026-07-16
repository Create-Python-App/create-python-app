# create-python-app

Composable scaffolding CLI for production-ready Python apps.

> **Status:** bootstrapping. Roadmap: [#1](https://github.com/Create-Python-App/create-python-app/issues/1).

## Monorepo layout (uv workspaces)

This repository is a **virtual uv workspace**: the root is not published; packages live under `packages/*` and share one `uv.lock` / `.venv`.

```text
create-python-app/          # virtual workspace root (no [project] table)
├── pyproject.toml          # [tool.uv.workspace] members = ["packages/*"]
├── uv.lock
├── .venv/                  # shared environment (gitignored later)
└── packages/
    ├── create-python-app-core/       # scaffolding engine
    └── create-awesome-python-app/    # CLI (depends on core via workspace)
```

### Setup

```bash
# Requires uv: https://docs.astral.sh/uv/
uv sync
```

### Reference

- [uv workspaces handbook](https://pydevtools.com/handbook/how-to/how-to-set-up-a-python-monorepo-with-uv-workspaces/)
- Node parity: [Create-Node-App/create-node-app](https://github.com/Create-Node-App/create-node-app)
