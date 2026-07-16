"""Merge pyproject.toml layers (CNA package.json merge parity)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.items import Array, Table

_DEP_NAME_RE = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)",
)


def dependency_name(spec: str) -> str:
    """Extract the distribution name from a PEP 508 requirement string."""
    match = _DEP_NAME_RE.match(spec)
    if not match:
        return spec.strip().lower()
    return match.group(1).lower().replace("_", "-")


def merge_dependency_lists(base: list[Any], overlay: list[Any]) -> list[str]:
    """Union dependency specs; later layer wins on the same package name."""
    by_name: dict[str, str] = {}
    order: list[str] = []
    for raw in [*base, *overlay]:
        spec = str(raw)
        name = dependency_name(spec)
        if name not in by_name:
            order.append(name)
        by_name[name] = spec
    return [by_name[name] for name in order]


_DEP_LIST_KEYS = frozenset({"dependencies", "optional-dependencies"})


def _is_mapping(value: Any) -> bool:
    return isinstance(value, (dict, Table))


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (list, Array)) and not isinstance(value, (str, bytes))


def merge_tables(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge TOML tables with dependency-list union rules."""
    result: dict[str, Any] = dict(base)
    for key, overlay_value in overlay.items():
        if key not in result:
            result[key] = overlay_value
            continue
        base_value = result[key]
        if key == "dependencies" and _is_sequence(base_value) and _is_sequence(overlay_value):
            result[key] = merge_dependency_lists(list(base_value), list(overlay_value))
        elif (
            key == "optional-dependencies"
            and _is_mapping(base_value)
            and _is_mapping(overlay_value)
        ):
            merged_opt: dict[str, Any] = dict(base_value)
            for opt_key, opt_val in overlay_value.items():
                if opt_key in merged_opt and _is_sequence(merged_opt[opt_key]) and _is_sequence(opt_val):
                    merged_opt[opt_key] = merge_dependency_lists(
                        list(merged_opt[opt_key]), list(opt_val)
                    )
                else:
                    merged_opt[opt_key] = opt_val
            result[key] = merged_opt
        elif key == "dependency-groups" and _is_mapping(base_value) and _is_mapping(overlay_value):
            merged_groups: dict[str, Any] = dict(base_value)
            for gkey, gval in overlay_value.items():
                if gkey in merged_groups and _is_sequence(merged_groups[gkey]) and _is_sequence(gval):
                    merged_groups[gkey] = merge_dependency_lists(
                        list(merged_groups[gkey]), list(gval)
                    )
                elif gkey in merged_groups and _is_mapping(merged_groups[gkey]) and _is_mapping(gval):
                    merged_groups[gkey] = merge_tables(dict(merged_groups[gkey]), dict(gval))
                else:
                    merged_groups[gkey] = gval
            result[key] = merged_groups
        elif _is_mapping(base_value) and _is_mapping(overlay_value):
            result[key] = merge_tables(dict(base_value), dict(overlay_value))
        else:
            # Later layer wins for scalars and non-dep arrays.
            result[key] = overlay_value
    return result


def merge_pyproject_text(base_text: str, overlay_text: str) -> str:
    """Merge two pyproject.toml documents; overlay wins conflicts."""
    base_doc = tomlkit.parse(base_text)
    overlay_doc = tomlkit.parse(overlay_text)
    merged = merge_tables(dict(base_doc), dict(overlay_doc))
    out = tomlkit.document()
    for key, value in merged.items():
        out[key] = value
    return tomlkit.dumps(out)


def merge_pyproject_into(existing: Path, overlay_text: str) -> str:
    """Merge overlay into an existing pyproject.toml file and return new text."""
    if existing.is_file():
        return merge_pyproject_text(existing.read_text(encoding="utf-8"), overlay_text)
    return overlay_text
