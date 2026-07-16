"""Scaffold orchestrator: copy layers → optional uv sync → git init."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from create_python_app_core.config import (
    CpaConfig,
    assert_directory_is_empty,
    load_cpa_config,
)
from create_python_app_core.errors import (
    CpaError,
    IncompatibleExtensionsError,
    ScaffoldAbortedError,
)
from create_python_app_core.git_cache import RefreshMode, download_repository
from create_python_app_core.loaders import merge_layers
from create_python_app_core.paths import ResolvedSource, resolve_source


def _run(cmd: list[str], *, cwd: Path) -> None:
    subprocess.check_call(cmd, cwd=str(cwd))


def init_git_repo(dest: Path) -> None:
    if (dest / ".git").exists():
        return
    _run(["git", "init"], cwd=dest)


def uv_sync(dest: Path) -> None:
    _run(["uv", "sync"], cwd=dest)


def _config_path(source: ResolvedSource, root: Path) -> Path:
    cfg_path = root / "cpa.config.json"
    if not cfg_path.is_file() and source.subdir:
        cfg_path = root / source.subdir / "cpa.config.json"
    return cfg_path


def build_scaffold_context(
    project_name: str,
    configs: list[CpaConfig],
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build Jinja context: projectName + customOption defaults + --set overrides."""
    context: dict[str, Any] = {"projectName": project_name}
    for cfg in configs:
        for opt in cfg.custom_options:
            if opt.key not in context and opt.default is not None:
                context[opt.key] = opt.default
    if options:
        set_map = options.get("set") or {}
        if isinstance(set_map, dict):
            context.update(set_map)
    return context


def _config_incompatible_list(cfg: CpaConfig) -> list[str]:
    raw = cfg.raw.get("incompatibleWith") or cfg.raw.get("incompatible_with") or []
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw]


def validate_config_incompatible_extensions(configs: list[CpaConfig]) -> None:
    """Fail when loaded cpa.config.json layers declare mutual incompatibility.

    The template config (first entry) is ignored; only addon/extend layers are
    checked. Matches are against each layer's ``name`` field (slug-like id).
    """
    addon_configs = [cfg for cfg in configs[1:] if cfg.name]
    names = {str(cfg.name) for cfg in addon_configs}
    pairs: list[tuple[str, str]] = []
    reported: set[tuple[str, str]] = set()
    for cfg in addon_configs:
        name = str(cfg.name)
        for other in _config_incompatible_list(cfg):
            if other not in names or other == name:
                continue
            first, second = sorted((name, other))
            key = (first, second)
            if key in reported:
                continue
            reported.add(key)
            pairs.append((name, other))
    if pairs:
        rendered = ", ".join(f"'{a}' ↔ '{b}'" for a, b in pairs)
        raise IncompatibleExtensionsError(
            "Incompatible extension combination from cpa.config.json: "
            f"{rendered}. Remove one of each conflicting pair and retry."
        )


def scaffold_project(
    project_directory: str,
    *,
    template: str,
    addons: list[str] | None = None,
    extend: list[str] | None = None,
    force: bool = False,
    install: bool = True,
    offline: bool = False,
    refresh: RefreshMode | None = None,
    keep_on_failure: bool = False,
    cache_dir: Path | None = None,
    options: dict[str, Any] | None = None,
) -> Path:
    """Create a project directory from template + addon layers."""
    dest = Path(project_directory).expanduser().resolve()
    assert_directory_is_empty(dest, force=force)
    dest.mkdir(parents=True, exist_ok=True)

    specs = [template, *(addons or []), *(extend or [])]
    layers: list[tuple[ResolvedSource, Path]] = []
    configs: list[CpaConfig] = []
    try:
        for spec in specs:
            source = resolve_source(spec, cache_dir=cache_dir)
            root = download_repository(
                source,
                offline=offline,
                refresh=refresh,
                cache_root=cache_dir,
            )
            layers.append((source, root))
            configs.append(load_cpa_config(_config_path(source, root)))

        validate_config_incompatible_extensions(configs)
        context = build_scaffold_context(dest.name, configs, options)
        merge_layers(layers, dest, context=context)

        if install and (dest / "pyproject.toml").is_file():
            uv_sync(dest)
        if os.environ.get("CPA_SKIP_GIT") != "1":
            init_git_repo(dest)
    except Exception as exc:
        if not keep_on_failure and dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        if isinstance(exc, CpaError):
            raise
        raise ScaffoldAbortedError(str(exc)) from exc
    return dest
