# ADR 0001: uv virtual workspace monorepo

## Decision

Use a virtual uv workspace root (`packages/*`, single `uv.lock`) instead of Poetry/PDM.

## Consequences

Shared `.venv`, consistent dependency resolution, fast CI via `astral-sh/setup-uv`.
