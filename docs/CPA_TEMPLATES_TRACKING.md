# Tracking: `cpa-templates` + website

Previously tracked by
[issue #44](https://github.com/Create-Python-App/create-python-app/issues/44)
(closed).

## Status

- [x] Create `Create-Python-App/cpa-templates`
- [x] Seed README + `templates.json`
- [x] `fastapi-starter` template + initial extensions
- [x] Wire catalog URL in CLI (`CPA_CATALOG_URL`, default raw GitHub URL)
- [x] Integration tests against `cpa-templates` checkout
- [x] Layered CI on `cpa-templates` (L0–L3) — always scaffold via `uvx` from PyPI ([cpa-templates#46](https://github.com/Create-Python-App/cpa-templates/issues/46))
- [ ] Website (optional, later)

## Repositories

| Repo | URL |
|------|-----|
| CLI monorepo | [create-python-app](https://github.com/Create-Python-App/create-python-app) |
| Template bank | [cpa-templates](https://github.com/Create-Python-App/cpa-templates) |

## CI contract (`cpa-templates`)

Template-bank CI **must** invoke the CLI as published on PyPI:

```sh
uvx create-awesome-python-app@latest …
```

It must **not** check out this monorepo or fall back to `uv run` against a local source tree. That way green Actions means the same binary users install works with the templates under test.

CLI CI in this repo stays focused on unit/lint/type, cross-platform scaffold
smoke via published `uvx`, and smoke-distribution (`uvx` / Docker / brew / AUR).

## CNA parity reference

| CNA | CPA |
|-----|-----|
| `create-node-app` | `create-python-app` |
| `cna-templates` | `cpa-templates` |
| `cna.config.json` | `cpa.config.json` |
| `~/.cache/cna` | `~/.cache/cpa` |
| Layered L0–L3 CI | Layered L0–L3 CI (`uvx` / PyPI) |
