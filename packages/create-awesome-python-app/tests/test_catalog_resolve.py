"""Catalog slug resolution tests."""

from __future__ import annotations

import pytest
from create_awesome_python_app.catalog import (
    CUSTOM_TEMPLATE_SENTINEL,
    CatalogResolutionError,
    build_template_choices,
    is_url_like,
    resolve_catalog_spec,
    resolve_catalog_specs,
    short_category_label,
)

SAMPLE_CATALOG = {
    "templates": [
        {
            "slug": "fastapi-starter",
            "url": "https://github.com/Create-Python-App/cpa-templates?subdir=templates/fastapi-starter",
        }
    ],
    "extensions": [
        {
            "slug": "github-setup",
            "url": "https://github.com/Create-Python-App/cpa-templates?subdir=extensions/github-setup",
        }
    ],
}


def test_is_url_like() -> None:
    assert is_url_like("https://github.com/org/repo")
    assert is_url_like("file:///tmp/foo")
    assert is_url_like("git@github.com:org/repo.git")
    assert not is_url_like("fastapi-starter")


def test_resolve_template_slug() -> None:
    url = resolve_catalog_spec("fastapi-starter", catalog=SAMPLE_CATALOG)
    assert "cpa-templates" in url
    assert "fastapi-starter" in url


def test_resolve_extension_slug() -> None:
    url = resolve_catalog_spec("github-setup", catalog=SAMPLE_CATALOG)
    assert "github-setup" in url


def test_resolve_url_unchanged() -> None:
    spec = "file:///tmp/template?subdir=foo"
    assert resolve_catalog_spec(spec, catalog=SAMPLE_CATALOG) == spec


def test_unknown_slug_raises() -> None:
    with pytest.raises(CatalogResolutionError, match="unknown-slug"):
        resolve_catalog_spec("unknown-slug", catalog=SAMPLE_CATALOG)


def test_resolve_catalog_specs_batch() -> None:
    resolved = resolve_catalog_specs(
        ["github-setup", "file:///ext"],
        catalog=SAMPLE_CATALOG,
    )
    assert len(resolved) == 2
    assert resolved[1] == "file:///ext"


def test_short_category_label_matches_cna_style() -> None:
    assert short_category_label("Backend Applications") == "Backend"
    assert short_category_label("User Acceptance Testing") == "UAT"


def test_build_template_choices_are_searchable() -> None:
    catalog = {
        "categories": [
            {
                "slug": "backend-applications",
                "name": "Backend Applications",
            }
        ],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "description": "Async API with OpenAPI docs",
                "url": "file:///templates/fastapi",
                "category": "backend-applications",
                "labels": ["FastAPI", "API", "uv"],
            }
        ],
    }

    choices = build_template_choices(catalog)
    first = choices[0]
    assert first.value == "file:///templates/fastapi"
    assert "FastAPI Starter" in first.title
    assert "OpenAPI" in first.title
    assert "uv" in first.title
    assert "openapi" in first.search
    assert "backend" in first.search
    assert "uv" in first.search
    assert choices[-1].value == CUSTOM_TEMPLATE_SENTINEL
