"""Template catalog fetch and listing."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from create_python_app_core.paths import default_cache_dir, resolve_source
from rich.console import Console
from rich.table import Table

from create_awesome_python_app import __version__

console = Console(stderr=True)


class CatalogResolutionError(ValueError):
    """Raised when a template or extension slug is not in the catalog."""

    def __init__(self, spec: str) -> None:
        self.spec = spec
        super().__init__(
            f"Invalid catalog slug: '{spec}'. "
            "Run --list-templates / --list-addons or pass a full URL."
        )


def is_url_like(spec: str) -> bool:
    """Return True when *spec* is already a URL or git SSH target."""
    return "://" in spec or spec.startswith("git@")


def resolve_catalog_spec(spec: str, *, catalog: dict[str, Any] | None = None) -> str:
    """Resolve a catalog slug to its registry URL, or return URL-like specs unchanged."""
    if is_url_like(spec):
        return spec
    data = catalog if catalog is not None else get_catalog_data()
    for entry in data.get("templates", []):
        if entry.get("slug") == spec:
            return str(entry["url"])
    for entry in data.get("extensions", data.get("addons", [])):
        if entry.get("slug") == spec:
            return str(entry["url"])
    raise CatalogResolutionError(spec)


def resolve_catalog_specs(
    specs: list[str], *, catalog: dict[str, Any] | None = None
) -> list[str]:
    return [resolve_catalog_spec(spec, catalog=catalog) for spec in specs]


DEFAULT_CATALOG_URL = "https://raw.githubusercontent.com/Create-Python-App/cpa-templates/main/templates.json"
CACHE_TTL_SECONDS = 3600
FETCH_TIMEOUT_SECONDS = 10
USER_AGENT = f"create-awesome-python-app/{__version__} (https://github.com/Create-Python-App/create-python-app)"

_FIXTURE = (
    Path(__file__).resolve().parents[4] / "fixtures" / "catalog" / "templates.json"
)

_memory_cache: dict[str, Any] | None = None
_memory_ts: float = 0.0


def catalog_url() -> str:
    return os.environ.get("CPA_CATALOG_URL", DEFAULT_CATALOG_URL)


def catalog_cache_path() -> Path:
    return default_cache_dir() / "catalog" / "templates.json"


def _read_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_fixture() -> dict[str, Any]:
    if _FIXTURE.is_file():
        return _read_json_file(_FIXTURE)
    return {"templates": [], "extensions": [], "categories": []}


def _read_disk_cache() -> dict[str, Any] | None:
    path = catalog_cache_path()
    if not path.is_file():
        return None
    try:
        return _read_json_file(path)
    except json.JSONDecodeError:
        return None


def _write_disk_cache(data: dict[str, Any]) -> None:
    path = catalog_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _fetch_file_url(url: str) -> dict[str, Any]:
    source = resolve_source(url)
    if source.local_path is None:
        raise OSError(f"Invalid file catalog URL: {url}")
    base = source.local_path
    if source.subdir:
        base = base / source.subdir
    if base.is_file():
        return _read_json_file(base)
    catalog_file = base / "templates.json"
    if not catalog_file.is_file():
        raise FileNotFoundError(f"Catalog not found: {catalog_file}")
    return _read_json_file(catalog_file)


def _fetch_remote(url: str) -> dict[str, Any]:
    if url.startswith("file://"):
        return _fetch_file_url(url)
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
        payload = resp.read().decode("utf-8")
    return json.loads(payload)


def get_catalog_data(*, force_refresh: bool = False) -> dict[str, Any]:
    """Load templates.json from remote URL, disk cache, or local fixture."""
    global _memory_cache, _memory_ts

    if (
        not force_refresh
        and _memory_cache is not None
        and os.environ.get("CPA_NO_CATALOG_CACHE") != "1"
        and time.time() - _memory_ts <= CACHE_TTL_SECONDS
    ):
        return _memory_cache

    if os.environ.get("CPA_CATALOG_FIXTURE") == "1":
        data = _read_fixture()
    else:
        url = catalog_url()
        try:
            data = _fetch_remote(url)
            _write_disk_cache(data)
        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
        ) as err:
            disk = _read_disk_cache()
            if disk is not None:
                console.print(
                    "[yellow][cpa] Could not refresh catalog "
                    f"({err}); using disk cache.[/yellow]"
                )
                data = disk
            else:
                fixture = _read_fixture()
                if fixture.get("templates"):
                    console.print(
                        "[yellow][cpa] Could not refresh catalog "
                        f"({err}); using fixture.[/yellow]"
                    )
                    data = fixture
                else:
                    raise RuntimeError(
                        f"Failed to load template catalog: {err}"
                    ) from err

    _memory_cache = data
    _memory_ts = time.time()
    return data


def reset_catalog_cache_for_tests() -> None:
    global _memory_cache, _memory_ts
    _memory_cache = None
    _memory_ts = 0.0


def list_templates() -> None:
    data = get_catalog_data()
    table = Table(title="Templates")
    table.add_column("slug")
    table.add_column("category")
    table.add_column("type")
    for t in data.get("templates", []):
        table.add_row(
            str(t.get("slug", "")),
            str(t.get("category", "")),
            str(t.get("type", "")),
        )
    console.print(table)


def list_addons(template_slug: str | None = None) -> None:
    data = get_catalog_data()
    template_type: str | None = None
    if template_slug:
        for t in data.get("templates", []):
            if t.get("slug") == template_slug:
                template_type = str(t.get("type", ""))
                break

    table = Table(title="Extensions")
    table.add_column("slug")
    table.add_column("category")
    table.add_column("type")
    for ext in data.get("extensions", data.get("addons", [])):
        ext_types = ext.get("type", [])
        if isinstance(ext_types, str):
            ext_types = [ext_types]
        if template_type and template_type not in ext_types:
            continue
        type_label = (
            ", ".join(ext_types) if isinstance(ext_types, list) else str(ext_types)
        )
        table.add_row(
            str(ext.get("slug", "")),
            str(ext.get("category", "")),
            type_label,
        )
    console.print(table)
