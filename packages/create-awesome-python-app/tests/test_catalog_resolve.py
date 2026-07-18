"""Catalog slug resolution tests."""

from __future__ import annotations

import pytest
from create_awesome_python_app.catalog import (
    CUSTOM_TEMPLATE_SENTINEL,
    CatalogResolutionError,
    IncompatibleExtensionsError,
    build_extension_choices,
    build_template_choices,
    find_incompatible_pairs,
    group_extension_choices,
    is_url_like,
    resolve_catalog_spec,
    resolve_catalog_specs,
    short_category_label,
    validate_extension_compatibility,
)
from create_awesome_python_app.prompt_style import (
    SearchableFormattedText,
    plain_title_text,
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
    title_text = plain_title_text(first.title)
    assert "FastAPI Starter" in title_text
    assert "OpenAPI" in title_text
    assert "uv" in title_text
    assert "openapi" in first.search
    assert "backend" in first.search
    assert "uv" in first.search
    assert choices[-1].value == CUSTOM_TEMPLATE_SENTINEL


def test_template_choice_titles_use_formatted_text(monkeypatch) -> None:
    """select() needs FormattedText tokens; raw ANSI shows as ^[[…m."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    catalog = {
        "categories": [
            {"slug": "backend-applications", "name": "Backend Applications"}
        ],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": "file:///templates/fastapi",
                "category": "backend-applications",
            }
        ],
    }
    title = build_template_choices(catalog)[0].title
    assert isinstance(title, SearchableFormattedText)
    assert "\033" not in plain_title_text(title)
    assert "FastAPI Starter" in plain_title_text(title)
    assert "fastapi" in title.lower()


def test_template_choice_titles_respect_no_color(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    catalog = {
        "categories": [
            {"slug": "backend-applications", "name": "Backend Applications"}
        ],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": "file:///templates/fastapi",
                "category": "backend-applications",
            }
        ],
    }
    title = build_template_choices(catalog)[0].title
    assert isinstance(title, str)
    assert "\033" not in title
    assert "FastAPI Starter" in title


def test_build_extension_choices_filters_by_template_type() -> None:
    catalog = {
        "categories": [
            {"slug": "ci", "name": "CI"},
            {"slug": "data", "name": "Data"},
        ],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": "file:///templates/fastapi",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [
            {
                "slug": "github-setup",
                "name": "GitHub Setup",
                "description": "Actions and Dependabot",
                "url": "file:///extensions/github",
                "type": ["fastapi-backend"],
                "category": "ci",
                "labels": ["GitHub", "CI"],
            },
            {
                "slug": "all-projects",
                "name": "All Projects",
                "url": "file:///extensions/all",
                "type": ["all"],
                "category": "data",
            },
            {
                "slug": "django-only",
                "name": "Django Only",
                "url": "file:///extensions/django",
                "type": ["django"],
                "category": "ci",
            },
        ],
    }

    choices = build_extension_choices(catalog, "file:///templates/fastapi")

    assert [choice.value for choice in choices] == [
        "file:///extensions/github",
        "file:///extensions/all",
    ]
    assert "dependabot" in choices[0].search
    assert "github" in choices[0].title.lower()


def test_group_extension_choices_preserves_category_order() -> None:
    catalog = {
        "categories": [
            {"slug": "ci", "name": "CI"},
            {"slug": "data", "name": "Data"},
        ],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": "file:///templates/fastapi",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [
            {
                "slug": "postgres",
                "name": "Postgres",
                "url": "file:///extensions/postgres",
                "type": ["fastapi-backend"],
                "category": "data",
            },
            {
                "slug": "github",
                "name": "GitHub",
                "url": "file:///extensions/github",
                "type": ["fastapi-backend"],
                "category": "ci",
            },
        ],
    }

    grouped = group_extension_choices(
        build_extension_choices(catalog, "file:///templates/fastapi")
    )

    assert list(grouped) == ["ci", "data"]
    assert grouped["ci"][0].value == "file:///extensions/github"


def test_validate_extension_compatibility_ok() -> None:
    catalog = {
        "extensions": [
            {
                "slug": "github-setup",
                "url": "file:///ext/github",
                "incompatibleWith": ["other"],
            },
            {"slug": "python-docker", "url": "file:///ext/docker"},
        ]
    }
    validate_extension_compatibility(["github-setup", "python-docker"], catalog=catalog)


def test_validate_extension_compatibility_fails_on_pair() -> None:
    catalog = {
        "extensions": [
            {
                "slug": "react-redux-saga",
                "url": "file:///ext/saga",
                "incompatibleWith": ["react-redux-thunk"],
            },
            {
                "slug": "react-redux-thunk",
                "url": "file:///ext/thunk",
                "incompatibleWith": ["react-redux-saga"],
            },
        ]
    }
    with pytest.raises(IncompatibleExtensionsError, match="react-redux-saga") as ei:
        validate_extension_compatibility(
            ["react-redux-saga", "file:///ext/thunk"],
            catalog=catalog,
        )
    assert ei.value.pairs == [("react-redux-saga", "react-redux-thunk")]


def test_find_incompatible_pairs_dedupes_symmetric_edges() -> None:
    catalog = {
        "extensions": [
            {
                "slug": "a",
                "url": "file:///a",
                "incompatibleWith": ["b"],
            },
            {
                "slug": "b",
                "url": "file:///b",
                "incompatibleWith": ["a"],
            },
        ]
    }
    pairs = find_incompatible_pairs(["a", "b"], catalog=catalog)
    assert pairs == [("a", "b")]
