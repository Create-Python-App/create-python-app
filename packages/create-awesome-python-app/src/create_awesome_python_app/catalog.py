"""Template catalog listing (stub URL / fixtures)."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

_FIXTURE = (
    Path(__file__).resolve().parents[4] / "fixtures" / "catalog" / "templates.json"
)


def _load() -> dict:
    if _FIXTURE.is_file():
        return json.loads(_FIXTURE.read_text(encoding="utf-8"))
    return {
        "templates": [{"slug": "example-cli", "category": "cli", "url": "file://."}],
        "addons": [{"slug": "ruff-setup", "category": "tooling"}],
    }


def list_templates() -> None:
    data = _load()
    table = Table(title="Templates")
    table.add_column("slug")
    table.add_column("category")
    for t in data.get("templates", []):
        table.add_row(t.get("slug", ""), t.get("category", ""))
    console.print(table)


def list_addons(template_slug: str | None = None) -> None:
    _ = template_slug
    data = _load()
    table = Table(title="Addons")
    table.add_column("slug")
    table.add_column("category")
    for t in data.get("addons", []):
        table.add_row(t.get("slug", ""), t.get("category", ""))
    console.print(table)
