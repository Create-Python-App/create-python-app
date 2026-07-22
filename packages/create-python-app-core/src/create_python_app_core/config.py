"""cpa.config.json schema and loaders."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from create_python_app_core.errors import (
    ConfigParseError,
    NonEmptyTargetDirectoryError,
)


@dataclass
class CpaCustomOption:
    key: str
    type: str = "string"
    message: str = ""
    default: Any = None


@dataclass
class CpaConfig:
    name: str | None = None
    custom_options: list[CpaCustomOption] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


def load_cpa_config(path: Path) -> CpaConfig:
    if not path.is_file():
        return CpaConfig()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigParseError(f"Invalid cpa.config.json: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigParseError("cpa.config.json must be a JSON object")
    options: list[CpaCustomOption] = []
    for item in data.get("customOptions") or data.get("custom_options") or []:
        if not isinstance(item, dict) or "key" not in item:
            raise ConfigParseError("custom option missing key")
        options.append(
            CpaCustomOption(
                key=str(item["key"]),
                type=str(item.get("type", "string")),
                message=str(item.get("message", "")),
                default=item.get("default"),
            )
        )
    return CpaConfig(
        name=data.get("name"),
        custom_options=options,
        raw=data,
    )


def assert_directory_is_empty(path: Path, *, force: bool = False) -> None:
    if force:
        return
    if path.exists() and any(path.iterdir()):
        raise NonEmptyTargetDirectoryError(
            f"Target directory is not empty: {path}. "
            "Use --force to continue, or pick a different directory name."
        )
