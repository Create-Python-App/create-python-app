"""Template catalog fetch and listing."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from create_python_app_core.paths import default_cache_dir, resolve_source
from rich.console import Console

from create_awesome_python_app import __version__
from create_awesome_python_app.prompt_style import (
    custom_template_title,
    template_title_tokens,
)

console = Console(stderr=True)

CUSTOM_TEMPLATE_SENTINEL = "__custom_template__"


@dataclass(frozen=True)
class TemplateChoice:
    """Searchable interactive template choice."""

    title: Any
    value: str
    search: str


@dataclass(frozen=True)
class ExtensionChoice:
    """Interactive extension choice grouped by catalog category."""

    title: str
    value: str
    search: str
    category_slug: str
    category_name: str
    category_order: int


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
    """Resolve a catalog slug to its registry URL."""
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


class IncompatibleExtensionsError(ValueError):
    """Raised when selected extensions declare mutual incompatibility."""

    def __init__(self, pairs: list[tuple[str, str]]) -> None:
        self.pairs = pairs
        rendered = ", ".join(f"'{a}' ↔ '{b}'" for a, b in pairs)
        super().__init__(
            "Incompatible extension combination: "
            f"{rendered}. Remove one of each conflicting pair and retry."
        )


def _extension_entries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    raw = catalog.get("extensions", catalog.get("addons", []))
    if not isinstance(raw, list):
        return []
    return [entry for entry in raw if isinstance(entry, dict)]


def find_extension_entry(catalog: dict[str, Any], spec: str) -> dict[str, Any] | None:
    """Find an extension by slug or URL."""
    for entry in _extension_entries(catalog):
        slug = str(entry.get("slug", ""))
        url = str(entry.get("url", ""))
        if spec in (slug, url):
            return entry
    return None


def find_incompatible_pairs(
    specs: list[str], *, catalog: dict[str, Any] | None = None
) -> list[tuple[str, str]]:
    """Return ordered (slug, conflicting_slug) pairs among *specs*."""
    data = catalog if catalog is not None else get_catalog_data()
    selected: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()
    for spec in specs:
        entry = find_extension_entry(data, spec)
        if entry is None:
            continue
        slug = str(entry.get("slug", ""))
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        selected.append(entry)

    selected_slugs = {str(entry.get("slug", "")) for entry in selected}
    pairs: list[tuple[str, str]] = []
    reported: set[tuple[str, str]] = set()
    for entry in selected:
        slug = str(entry.get("slug", ""))
        raw = entry.get("incompatibleWith") or entry.get("incompatible_with") or []
        if not isinstance(raw, list):
            continue
        for other in raw:
            other_slug = str(other)
            if other_slug not in selected_slugs or other_slug == slug:
                continue
            first, second = sorted((slug, other_slug))
            key = (first, second)
            if key in reported:
                continue
            reported.add(key)
            pairs.append((slug, other_slug))
    return pairs


def validate_extension_compatibility(
    specs: list[str], *, catalog: dict[str, Any] | None = None
) -> None:
    """Fail fast when selected catalog extensions are mutually incompatible."""
    pairs = find_incompatible_pairs(specs, catalog=catalog)
    if pairs:
        raise IncompatibleExtensionsError(pairs)


@dataclass(frozen=True)
class CategoryInfo:
    """Catalog category with optional rich metadata (CNA parity)."""

    slug: str
    name: str
    description: str = ""
    details: str = ""
    labels: tuple[str, ...] = ()


def short_category_label(category_name: str) -> str:
    """Derive a compact badge label from a catalog category name."""
    stop_words = {"Applications", "Application", "Boilerplate"}
    words = [word for word in category_name.split() if word not in stop_words]
    if len(words) >= 3:
        return "".join(word[:1].upper() for word in words)
    return " ".join(words[:2]) or category_name


def category_index(data: dict[str, Any]) -> dict[str, CategoryInfo]:
    """Index categories by slug, including description/details/labels."""
    out: dict[str, CategoryInfo] = {}
    for raw in data.get("categories", []):
        if not isinstance(raw, dict):
            continue
        slug = str(raw.get("slug", "")).strip()
        if not slug:
            continue
        labels_raw = raw.get("labels", [])
        labels = (
            tuple(str(label) for label in labels_raw)
            if isinstance(labels_raw, list)
            else ()
        )
        out[slug] = CategoryInfo(
            slug=slug,
            name=str(raw.get("name", slug)),
            description=str(raw.get("description", "")).strip(),
            details=str(raw.get("details", "")).strip(),
            labels=labels,
        )
    return out


def get_category_data(data: dict[str, Any], slug: str) -> CategoryInfo | None:
    return category_index(data).get(slug)


def format_category_choice_title(info: CategoryInfo, extension_count: int) -> str:
    """Human title for the interactive extension-category picker."""
    noun = "extension" if extension_count == 1 else "extensions"
    title = f"{info.name} ({extension_count} {noun})"
    if info.description:
        title = f"{title} — {info.description}"
    if info.labels:
        title = f"{title} · {', '.join(info.labels[:3])}"
    return title


def _category_map(data: dict[str, Any]) -> dict[str, str]:
    return {slug: info.name for slug, info in category_index(data).items()}


def _search_text(template: dict[str, Any], category_name: str) -> str:
    labels = template.get("labels", [])
    if not isinstance(labels, list):
        labels = []
    tokens = [
        template.get("slug", ""),
        template.get("name", ""),
        template.get("description", ""),
        template.get("category", ""),
        category_name,
        *labels,
    ]
    return " ".join(str(token) for token in tokens if token).lower()


def _catalog_category_order(data: dict[str, Any]) -> dict[str, int]:
    return {
        str(category.get("slug", "")): index
        for index, category in enumerate(data.get("categories", []))
    }


def _entry_type_values(entry: dict[str, Any]) -> list[str]:
    raw_type = entry.get("type", [])
    if isinstance(raw_type, str):
        return [raw_type]
    if isinstance(raw_type, list):
        return [str(item) for item in raw_type]
    return []


def find_template_by_url(
    data: dict[str, Any], template_url: str
) -> dict[str, Any] | None:
    """Return the catalog template entry for a resolved template URL."""
    for template in data.get("templates", []):
        if isinstance(template, dict) and template.get("url") == template_url:
            return template
    return None


def build_template_choices(data: dict[str, Any]) -> list[TemplateChoice]:
    """Build CNA-style searchable template choices for interactive mode."""
    categories = _category_map(data)
    choices: list[TemplateChoice] = []
    templates = sorted(
        (item for item in data.get("templates", []) if isinstance(item, dict)),
        key=lambda item: (
            list(categories).index(str(item.get("category", "")))
            if str(item.get("category", "")) in categories
            else len(categories),
            str(item.get("name", item.get("slug", ""))).lower(),
        ),
    )
    for template in templates:
        if not isinstance(template, dict):
            continue
        template_url = str(template.get("url", ""))
        if not template_url:
            continue
        category_slug = str(template.get("category", "custom"))
        category_name = categories.get(category_slug, category_slug)
        badge = short_category_label(category_name).ljust(10)[:10]
        slug = str(template.get("slug", ""))
        labels_raw = template.get("labels", [])
        labels = (
            [str(label) for label in labels_raw[:3]]
            if isinstance(labels_raw, list)
            else []
        )
        description = str(template.get("description", "")).strip()
        name = str(template.get("name", slug))
        search = _search_text(template, category_name)
        # FormattedText tokens (not raw ANSI): select() prints str titles
        # literally, which showed ^[[1;94m… in terminals.
        title = template_title_tokens(
            category_slug=category_slug,
            badge=badge,
            name=name,
            slug=slug,
            labels=labels,
            description=description,
            search=search,
        )
        choices.append(
            TemplateChoice(
                title=title,
                value=template_url,
                search=search,
            )
        )

    custom_search = "custom own template url github file"
    choices.append(
        TemplateChoice(
            title=custom_template_title(custom_search),
            value=CUSTOM_TEMPLATE_SENTINEL,
            search=custom_search,
        )
    )
    return choices


def build_extension_choices(
    data: dict[str, Any], template_url: str
) -> list[ExtensionChoice]:
    """Build CNA-style extension choices compatible with the selected template."""
    categories = _category_map(data)
    category_order = _catalog_category_order(data)
    template = find_template_by_url(data, template_url)
    template_types = _entry_type_values(template or {})
    if not template_types:
        template_types = ["custom"]

    choices: list[ExtensionChoice] = []
    for extension in data.get("extensions", data.get("addons", [])):
        if not isinstance(extension, dict):
            continue
        extension_types = _entry_type_values(extension)
        if not any(
            ext_type in template_types or ext_type == "all"
            for ext_type in extension_types
        ):
            continue
        extension_url = str(extension.get("url", ""))
        if not extension_url:
            continue
        category_slug = str(extension.get("category", "custom"))
        category_name = categories.get(category_slug, category_slug)
        labels = extension.get("labels", [])
        label_suffix = ""
        if isinstance(labels, list) and labels:
            label_suffix = " · " + ", ".join(str(label) for label in labels[:3])
        description = str(extension.get("description", "")).strip()
        description_suffix = f" — {description}" if description else ""
        slug = str(extension.get("slug", ""))
        title = f"{extension.get('name', slug)} ({slug}){label_suffix}"
        choices.append(
            ExtensionChoice(
                title=f"{title}{description_suffix}",
                value=extension_url,
                search=_search_text(extension, category_name),
                category_slug=category_slug,
                category_name=category_name,
                category_order=category_order.get(category_slug, len(category_order)),
            )
        )

    return sorted(
        choices,
        key=lambda choice: (choice.category_order, choice.title.lower()),
    )


def group_extension_choices(
    choices: list[ExtensionChoice],
) -> dict[str, list[ExtensionChoice]]:
    """Group extension choices by category while preserving sorted order."""
    grouped: dict[str, list[ExtensionChoice]] = {}
    for choice in choices:
        grouped.setdefault(choice.category_slug, []).append(choice)
    return grouped


DEFAULT_CATALOG_URL = "https://raw.githubusercontent.com/Create-Python-App/cpa-templates/main/templates.json"
CACHE_TTL_SECONDS = 3600
FETCH_TIMEOUT_SECONDS = 10
USER_AGENT = f"create-awesome-python-app/{__version__} (https://github.com/Create-Python-App/create-python-app)"

_AUTO_FIXTURE_DIR = Path(__file__).resolve().parents[4]
_SENTINEL = object()
_fixture_root_override: Path | None | object = _SENTINEL

_memory_cache: dict[str, Any] | None = None
_memory_ts: float = 0.0


def catalog_url() -> str:
    return os.environ.get("CPA_CATALOG_URL", DEFAULT_CATALOG_URL)


def catalog_cache_path() -> Path:
    return default_cache_dir() / "catalog" / "templates.json"


def resolve_fixture_root() -> Path | None:
    """Resolve the repo root that contains ``fixtures/catalog/templates.json``.

    Priority: ``CPA_FIXTURE_DIR`` → walk-up from package → ``cwd``.
    """
    if _fixture_root_override is not _SENTINEL:
        return _fixture_root_override  # type: ignore[return-value]

    env = os.environ.get("CPA_FIXTURE_DIR", "").strip()
    if env:
        return Path(env).expanduser().resolve()

    def _has_fixture_catalog(root: Path) -> bool:
        return (root / "fixtures" / "catalog" / "templates.json").is_file()

    if _has_fixture_catalog(_AUTO_FIXTURE_DIR):
        return _AUTO_FIXTURE_DIR

    # Editable / site-packages layouts vary; walk up from this file.
    for parent in Path(__file__).resolve().parents:
        if _has_fixture_catalog(parent):
            return parent

    cwd = Path.cwd()
    if _has_fixture_catalog(cwd):
        return cwd
    return None


def set_fixture_root_for_tests(root: Path | None) -> None:
    """Override fixture root (test helper)."""
    global _fixture_root_override
    _fixture_root_override = root


def reset_fixture_root_for_tests() -> None:
    global _fixture_root_override
    _fixture_root_override = _SENTINEL


def fixture_catalog_path() -> Path | None:
    root = resolve_fixture_root()
    if root is None:
        return None
    return root / "fixtures" / "catalog" / "templates.json"


def _read_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_fixture() -> dict[str, Any]:
    path = fixture_catalog_path()
    if path is not None and path.is_file():
        return _read_json_file(path)
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

    if os.environ.get("CPA_CATALOG_FIXTURE") == "1":
        path = fixture_catalog_path()
        if path is None or not path.is_file():
            raise RuntimeError(
                "Fixture mode is enabled (CPA_CATALOG_FIXTURE=1) but the fixture "
                "root could not be resolved. Set CPA_FIXTURE_DIR to the repo root "
                "containing fixtures/catalog/templates.json."
            )
        data = _read_fixture()
        _memory_cache = data
        _memory_ts = time.time()
        return data

    if (
        not force_refresh
        and _memory_cache is not None
        and os.environ.get("CPA_NO_CATALOG_CACHE") != "1"
        and time.time() - _memory_ts <= CACHE_TTL_SECONDS
    ):
        return _memory_cache

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
                raise RuntimeError(f"Failed to load template catalog: {err}") from err

    _memory_cache = data
    _memory_ts = time.time()
    return data


def reset_catalog_cache_for_tests() -> None:
    global _memory_cache, _memory_ts
    _memory_cache = None
    _memory_ts = 0.0


def _template_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [t for t in data.get("templates", []) if isinstance(t, dict)]


def _require_known_category(
    categories: dict[str, CategoryInfo],
    templates: list[dict[str, Any]],
    category: str,
) -> None:
    known = {str(t.get("category", "")) for t in templates} | set(categories)
    known.discard("")
    if category not in known:
        raise CatalogResolutionError(
            f"Unknown category '{category}'. "
            f"Available: {', '.join(sorted(known)) or '(none)'}"
        )


def _template_json(template: dict[str, Any]) -> dict[str, Any]:
    labels = template.get("labels", [])
    return {
        "slug": str(template.get("slug", "")),
        "name": str(template.get("name", template.get("slug", ""))),
        "description": str(template.get("description", "")),
        "category": str(template.get("category", "")),
        "labels": [str(x) for x in labels] if isinstance(labels, list) else [],
    }


def templates_view(category: str | None = None) -> dict[str, Any]:
    """Machine-readable template listing (``--list-templates --json``)."""
    data = get_catalog_data()
    categories = category_index(data)
    templates = _template_entries(data)
    if category:
        _require_known_category(categories, templates, category)
        templates = [t for t in templates if str(t.get("category", "")) == category]
    return {"templates": [_template_json(t) for t in templates]}


def list_templates(category: str | None = None) -> None:
    data = get_catalog_data()
    categories = category_index(data)
    templates = _template_entries(data)
    if category:
        _require_known_category(categories, templates, category)
        templates = [t for t in templates if str(t.get("category", "")) == category]

    console.print("[bold blue]\nAvailable Templates:[/bold blue]")
    # Preserve catalog category order, then any unknown slugs.
    ordered_slugs = [category] if category else list(categories)
    seen: set[str] = set()
    for slug in ordered_slugs:
        seen.add(slug)
        group = [t for t in templates if str(t.get("category", "")) == slug]
        if not group:
            continue
        info = categories.get(slug) or CategoryInfo(slug=slug, name=slug)
        console.print(f"[bold green]\n{info.name}:[/bold green]")
        if info.description:
            console.print(f"  {info.description}")
        if info.details:
            console.print(f"  [dim]{info.details}[/dim]")
        if info.labels:
            console.print(f"  [dim]Keywords: {', '.join(info.labels)}[/dim]")
        for template in group:
            name = str(template.get("name", template.get("slug", "")))
            tslug = str(template.get("slug", ""))
            console.print(f"  [yellow]{name}[/yellow] ([cyan]{tslug}[/cyan])")
            desc = str(template.get("description", "")).strip()
            if desc:
                console.print(f"    {desc}")
            labels = template.get("labels", [])
            if isinstance(labels, list) and labels:
                console.print(f"    Keywords: {', '.join(str(x) for x in labels)}")

    orphans = (
        []
        if category
        else [t for t in templates if str(t.get("category", "")) not in seen]
    )
    if orphans:
        console.print("[bold green]\nOther:[/bold green]")
        for template in orphans:
            name = str(template.get("name", template.get("slug", "")))
            tslug = str(template.get("slug", ""))
            console.print(f"  [yellow]{name}[/yellow] ([cyan]{tslug}[/cyan])")


def _template_type_for(data: dict[str, Any], template_slug: str | None) -> str | None:
    if not template_slug:
        return None
    for t in data.get("templates", []):
        if isinstance(t, dict) and t.get("slug") == template_slug:
            return str(t.get("type", ""))
    return None


def _addon_entries(
    data: dict[str, Any], template_slug: str | None
) -> list[dict[str, Any]]:
    template_type = _template_type_for(data, template_slug)
    entries = []
    for ext in data.get("extensions", data.get("addons", [])):
        if not isinstance(ext, dict):
            continue
        ext_types = ext.get("type", [])
        if isinstance(ext_types, str):
            ext_types = [ext_types]
        if template_type and template_type not in ext_types:
            continue
        entries.append(ext)
    return entries


def _addon_json(ext: dict[str, Any]) -> dict[str, Any]:
    labels = ext.get("labels", [])
    ext_type = ext.get("type", [])
    return {
        "slug": str(ext.get("slug", "")),
        "name": str(ext.get("name", ext.get("slug", ""))),
        "description": str(ext.get("description", "")),
        "category": str(ext.get("category", "custom")),
        "type": [str(x) for x in ext_type]
        if isinstance(ext_type, list)
        else [str(ext_type)],
        "labels": [str(x) for x in labels] if isinstance(labels, list) else [],
    }


def addons_view(template_slug: str | None = None) -> dict[str, Any]:
    """Machine-readable addon listing (``--list-addons --json``)."""
    data = get_catalog_data()
    return {
        "template": template_slug,
        "addons": [_addon_json(e) for e in _addon_entries(data, template_slug)],
    }


def list_addons(template_slug: str | None = None) -> None:
    data = get_catalog_data()
    categories = category_index(data)

    console.print("[bold blue]\nAvailable Addons:[/bold blue]")
    if template_slug:
        console.print(
            f"[bold green]\nCompatible with template: {template_slug}[/bold green]"
        )

    extensions = _addon_entries(data, template_slug)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ext in extensions:
        slug = str(ext.get("category", "custom"))
        grouped.setdefault(slug, []).append(ext)

    for slug in list(categories) + [s for s in grouped if s not in categories]:
        group = grouped.get(slug)
        if not group:
            continue
        info = categories.get(slug) or CategoryInfo(slug=slug, name=slug)
        console.print(f"[bold green]\n{info.name}:[/bold green]")
        if info.description:
            console.print(f"  {info.description}")
        if info.details:
            console.print(f"  [dim]{info.details}[/dim]")
        if info.labels:
            console.print(f"  [dim]Keywords: {', '.join(info.labels)}[/dim]")
        for ext in group:
            name = str(ext.get("name", ext.get("slug", "")))
            eslug = str(ext.get("slug", ""))
            console.print(f"  [yellow]{name}[/yellow] ([cyan]{eslug}[/cyan])")
            desc = str(ext.get("description", "")).strip()
            if desc:
                console.print(f"    {desc}")
            labels = ext.get("labels", [])
            if isinstance(labels, list) and labels:
                console.print(f"    Keywords: {', '.join(str(x) for x in labels)}")
