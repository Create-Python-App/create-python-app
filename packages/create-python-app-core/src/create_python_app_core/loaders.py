"""Template/extension file loaders and merge model."""

from __future__ import annotations

import shutil
from pathlib import Path

from create_python_app_core.errors import ManifestLoadError
from create_python_app_core.paths import ResolvedSource, get_template_dir_path


def copy_tree(src: Path, dest: Path, *, overwrite: bool = True) -> list[Path]:
    """Copy files from src into dest. Returns list of written paths."""
    written: list[Path] = []
    if not src.is_dir():
        raise ManifestLoadError(f"template directory not found: {src}")
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        target = dest / rel
        if target.exists() and not overwrite:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        written.append(target)
    return written


def load_layer(
    source: ResolvedSource,
    root: Path,
    dest: Path,
    *,
    overwrite: bool = True,
) -> list[Path]:
    """Load one template/extension layer into dest."""
    template_root = get_template_dir_path(source, root)
    return copy_tree(template_root, dest, overwrite=overwrite)


def merge_layers(
    layers: list[tuple[ResolvedSource, Path]],
    dest: Path,
) -> list[Path]:
    """Apply layers in order: template → addons → extend (later wins)."""
    written: list[Path] = []
    for source, root in layers:
        written.extend(load_layer(source, root, dest, overwrite=True))
    return written
