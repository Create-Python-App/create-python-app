# `cpa.config.json` vs `cna.config.json`

| Concern | CNA | CPA |
|---------|-----|-----|
| Config file | `cna.config.json` | `cpa.config.json` |
| Manifest | `package.json` | `pyproject.toml` |
| Installer | npm/yarn/pnpm/bun | `uv sync` |
| Lint defaults | ESLint | Ruff |
| Custom options | `customOptions[]` | same shape |

See also [cpa-config-schema.md](./cpa-config-schema.md).

## Minimal FastAPI stub example

```json
{
  "name": "fastapi-starter",
  "customOptions": [
    {"key": "projectName", "type": "string", "default": "my-api"}
  ]
}
```
