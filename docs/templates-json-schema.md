# `templates.json` schema (CPA)

Parity with [cna-templates `templates.json`](https://github.com/Create-Node-App/cna-templates).

```json
{
  "templates": [
    {
      "slug": "fastapi-starter",
      "name": "FastAPI Starter",
      "category": "backend",
      "url": "https://github.com/Create-Python-App/cpa-templates?subdir=templates/fastapi-starter",
      "description": "Minimal FastAPI app with uv"
    }
  ],
  "addons": [
    {
      "slug": "ruff-setup",
      "name": "Ruff",
      "category": "tooling",
      "url": "https://github.com/Create-Python-App/cpa-templates?subdir=extensions/ruff-setup"
    }
  ]
}
```

## Differences from Node

- URLs point at Python templates (pyproject/uv/ruff) instead of package.json/npm
- Compatibility metadata should list Python ranges instead of Node engines
