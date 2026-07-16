"""Catalog fetch tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from create_awesome_python_app.catalog import (
    DEFAULT_CATALOG_URL,
    catalog_cache_path,
    catalog_url,
    get_catalog_data,
    reset_catalog_cache_for_tests,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3] / "fixtures" / "catalog" / "templates.json"
)
REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_CPA_TEMPLATES = (REPO_ROOT.parent / "cpa-templates").resolve()
CPA_TEMPLATES_ROOT = Path(
    os.environ.get("CPA_TEMPLATES_ROOT", str(_DEFAULT_CPA_TEMPLATES))
).resolve()


@pytest.fixture(autouse=True)
def _reset_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reset_catalog_cache_for_tests()
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cache"))


def test_default_catalog_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CPA_CATALOG_URL", raising=False)
    assert "Create-Python-App/cpa-templates" in catalog_url()
    monkeypatch.setenv("CPA_CATALOG_URL", "https://example.com/templates.json")
    assert catalog_url() == "https://example.com/templates.json"


def test_get_catalog_data_fetches_and_caches(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    class FakeResponse:
        def read(self) -> bytes:
            return json.dumps(payload).encode("utf-8")

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with patch(
        "create_awesome_python_app.catalog.urllib.request.urlopen",
        return_value=FakeResponse(),
    ):
        data = get_catalog_data(force_refresh=True)

    assert any(t["slug"] == "fastapi-starter" for t in data["templates"])
    assert catalog_cache_path().is_file()


def test_get_catalog_data_fixture_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    data = get_catalog_data(force_refresh=True)
    assert data["templates"]


def test_get_catalog_data_disk_fallback_on_network_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"templates": [{"slug": "cached"}], "extensions": [], "categories": []}
    cache_file = catalog_cache_path()
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(payload), encoding="utf-8")

    with patch(
        "create_awesome_python_app.catalog._fetch_remote",
        side_effect=OSError("network down"),
    ):
        data = get_catalog_data(force_refresh=True)

    assert data["templates"][0]["slug"] == "cached"


def test_local_cpa_templates_catalog_includes_typed_fastapi_template() -> None:
    catalog_path = CPA_TEMPLATES_ROOT / "templates.json"
    assert catalog_path.is_file()

    payload = json.loads(catalog_path.read_text(encoding="utf-8"))

    assert any(template["slug"] == "fastapi-typed-starter" for template in payload["templates"])


def test_default_url_points_to_cpa_templates() -> None:
    assert DEFAULT_CATALOG_URL.endswith("/cpa-templates/main/templates.json")
