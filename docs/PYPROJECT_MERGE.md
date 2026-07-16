# pyproject.toml merge rules

When scaffolding layers include a `pyproject.toml`, CPA **merges** into an existing destination file instead of overwriting it.

## Rules

| Key | Behavior |
|-----|----------|
| `[project].dependencies` | Union by package name; **later layer wins** on version conflict |
| `[project].optional-dependencies.*` | Same union-per-group |
| `[dependency-groups].*` | Same union-per-group (uv) |
| Nested tables (`[tool.*]`, etc.) | Deep merge; scalars: later wins |
| Other arrays | Later layer replaces |

## Example

Base template:

```toml
[project]
name = "my-api"
dependencies = ["fastapi>=0.115"]
```

Extension overlay:

```toml
[project]
dependencies = ["psycopg[binary]>=3.2"]

[dependency-groups]
dev = ["ruff>=0.8"]
```

Result keeps `name`, unions dependencies, and adds the dev group.
