# Contributing to Create Awesome Python App

Thanks for contributing! Please follow the [Code of Conduct](./.github/CODE_OF_CONDUCT.md).

## Local development

```bash
git clone https://github.com/Create-Python-App/create-python-app.git
cd create-python-app
uv sync --group dev
uv run pre-commit install
make test
make lint
make typecheck
```

## Testing with fixtures

The CLI can run entirely offline for catalog-related tests by switching into fixture mode. Use `--fixture` to opt in for a single run, or set the environment variables below for the current shell.

- `--fixture` enables fixture mode and optionally accepts a directory argument. When you pass a directory, it sets `CPA_FIXTURE_DIR` for that run.
- `CPA_CATALOG_FIXTURE=1` enables the same offline catalog path without using the flag.
- `CPA_FIXTURE_DIR=/path/to/repo` points to the repository root that contains the fixture tree. The CLI looks for `fixtures/catalog/templates.json` there, and local template sources live under `fixtures/templates/` and `fixtures/extensions/`.

The repository ships a small fixture catalog in [fixtures/catalog/templates.json](fixtures/catalog/templates.json) so you can list templates or run a smoke scaffold without hitting GitHub raw URLs.

### List templates offline

From the repository root, this works without network access:

```bash
uv run create-awesome-python-app --fixture . --list-templates
```

### Smoke scaffold with fixtures

This uses the local fixture template under [fixtures/templates/example-cli](fixtures/templates/example-cli):

```bash
repo="$(pwd)"
uv run create-awesome-python-app --fixture "$repo" --template "file://$repo/fixtures/templates/example-cli" --no-install --no-interactive ./tmp-cpa-smoke
```

If you prefer environment variables instead of the flag, the equivalent is:

```bash
export CPA_CATALOG_FIXTURE=1
export CPA_FIXTURE_DIR="$repo"
uv run create-awesome-python-app --list-templates
```

The fixture behavior is exercised in [packages/create-awesome-python-app/tests/test_cli.py](packages/create-awesome-python-app/tests/test_cli.py) and [packages/create-awesome-python-app/tests/test_catalog_fetch.py](packages/create-awesome-python-app/tests/test_catalog_fetch.py).

## Pull requests

1. Branch from `main`
2. Keep changes focused; link an issue
3. Use [Conventional Commits](https://www.conventionalcommits.org/)
4. Ensure tests/lint/typecheck pass
5. Fill out the PR template

## Templates

Template and extension authoring lives in [`cpa-templates`](https://github.com/Create-Python-App/cpa-templates).

To test scaffolding against a local `cpa-templates` checkout:

```bash
export CPA_TEMPLATES_ROOT=/path/to/cpa-templates
uv run pytest packages/create-awesome-python-app/tests/test_cpa_templates_integration.py -v
```

The catalog is fetched from `cpa-templates` `templates.json` (override with `CPA_CATALOG_URL`).
