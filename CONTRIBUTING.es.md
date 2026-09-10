# Contribuir a Create Awesome Python App (resumen en español)

> El inglés es la fuente de verdad. Esta es una traducción condensada de las
> secciones de incorporación de `CONTRIBUTING.md`.

Gracias por contribuir. Sigue el
[Código de Conducta](./.github/CODE_OF_CONDUCT.md).

## Desarrollo local

```bash
git clone https://github.com/Create-Python-App/create-python-app.git
cd create-python-app
uv sync --group dev
uv run pre-commit install
make test
make lint
make typecheck
```

## Probar con fixtures (sin red)

El CLI puede funcionar sin conexión con el catálogo de fixtures:

```bash
uv run create-awesome-python-app --fixture . --list-templates
```

## Pull requests

1. Crea tu rama desde `main`.
2. Cambios enfocados; enlaza el issue correspondiente.
3. Usa [Conventional Commits](https://www.conventionalcommits.org/) (mensajes en inglés).
4. Asegúrate de que pasen los tests, el lint (`ruff`) y los tipos (`pyright`).
5. Completa la plantilla del PR (en inglés).

## Dónde vive cada cosa

- Motor del CLI: `packages/`.
- Plantillas y extensiones: [`cpa-templates`](https://github.com/Create-Python-App/cpa-templates).
- Documentación del sitio: [`website`](https://github.com/Create-Python-App/website).
