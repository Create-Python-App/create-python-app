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
