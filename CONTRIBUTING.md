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

Template bank work will live in `cpa-templates` (tracked in #44). Until then use `fixtures/`.
