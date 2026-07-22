"""Template/extension file loaders and merge model."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

from jinja2 import Environment, StrictUndefined, TemplateError

from create_python_app_core.errors import ManifestLoadError, ScaffoldAbortedError
from create_python_app_core.paths import ResolvedSource, get_template_dir_path
from create_python_app_core.pyproject_merge import merge_pyproject_into

_JINJA = Environment(
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    autoescape=False,
)

CopyMethod = Literal["reflink", "hardlink", "copy"]


def copy_file_efficient(
    src: Path,
    dest: Path,
    *,
    allow_hardlink: bool = True,
) -> CopyMethod:
    """Copy a file using reflink → hardlink → ``shutil.copy2`` (CNA parity).

    Hardlinks are skipped when ``allow_hardlink`` is False (e.g. files that will
    be mutated by template rendering) or when ``CPA_COPY_HARDLINK=0``.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()

    hardlink_ok = allow_hardlink and os.environ.get("CPA_COPY_HARDLINK", "1") != "0"

    if os.name != "nt":
        # 1) Reflink / clonefile (near-instant CoW on Btrfs/XFS/ZFS/APFS).
        for args in (
            ["cp", "-c", "--", str(src), str(dest)],  # macOS clonefile
            ["cp", "--reflink=auto", "--", str(src), str(dest)],  # GNU
        ):
            try:
                subprocess.run(args, check=True, capture_output=True)
                if dest.is_file():
                    shutil.copystat(src, dest, follow_symlinks=True)
                    return "reflink"
            except (FileNotFoundError, subprocess.CalledProcessError, OSError):
                if dest.exists():
                    dest.unlink(missing_ok=True)

        # 2) Hardlink (same inode — avoided for rendered/mutated files).
        if hardlink_ok:
            try:
                os.link(src, dest)
                return "hardlink"
            except OSError:
                if dest.exists():
                    dest.unlink(missing_ok=True)

    # 3) Full recursive metadata-preserving copy.
    shutil.copy2(src, dest)
    return "copy"


def _mode_from_path(rel: Path) -> str:
    name = rel.name
    if name.endswith(".append.template") or name.endswith(".template.append"):
        return "appendTemplate"
    if name.endswith(".append"):
        return "append"
    if name.endswith(".template"):
        return "copyTemplate"
    return "copy"


def _output_rel(rel: Path) -> Path:
    """Strip processing suffixes from a relative path."""
    name = rel.name
    for suffix in (".append.template", ".template.append", ".template", ".append"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return rel.with_name(name)


def render_template(content: str, context: dict[str, Any], *, path: str) -> str:
    """Render Jinja2 content with StrictUndefined."""
    try:
        return _JINJA.from_string(content).render(**context)
    except TemplateError as exc:
        raise ScaffoldAbortedError(f"Template render failed for {path}: {exc}") from exc


def _write_bytes(target: Path, data: bytes, *, append: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "ab" if append else "wb"
    with target.open(mode) as fh:
        fh.write(data)


def _write_text(target: Path, text: str, *, append: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with target.open(mode, encoding="utf-8") as fh:
        fh.write(text)


def process_file(
    src: Path,
    dest_root: Path,
    rel: Path,
    *,
    context: dict[str, Any],
    overwrite: bool = True,
) -> Path | None:
    """Copy / render / append one file into dest_root. Returns written path or None."""
    mode = _mode_from_path(rel)
    out_rel = _output_rel(rel)
    target = dest_root / out_rel

    if mode == "append":
        content = src.read_text(encoding="utf-8")
        _write_text(target, content, append=True)
        return target

    if mode in {"copyTemplate", "appendTemplate"}:
        rendered = render_template(
            src.read_text(encoding="utf-8"),
            context,
            path=str(rel),
        )
        append = mode == "appendTemplate"
        if out_rel.name == "pyproject.toml" and not append:
            text = merge_pyproject_into(target, rendered)
            _write_text(target, text, append=False)
            return target
        if target.exists() and not overwrite and not append:
            return None
        _write_text(target, rendered, append=append)
        return target

    # plain copy
    if out_rel.name == "pyproject.toml":
        text = merge_pyproject_into(target, src.read_text(encoding="utf-8"))
        _write_text(target, text, append=False)
        return target

    if target.exists() and not overwrite:
        return None
    # Plain files: reflink → hardlink → copy2. Never hardlink .template
    # paths (handled above); allow_hardlink stays True for immutable copies.
    copy_file_efficient(src, target, allow_hardlink=True)
    return target


def copy_tree(
    src: Path,
    dest: Path,
    *,
    overwrite: bool = True,
    context: dict[str, Any] | None = None,
) -> list[Path]:
    """Copy files from src into dest with .template / .append processing."""
    written: list[Path] = []
    if not src.is_dir():
        raise ManifestLoadError(f"template directory not found: {src}")
    dest.mkdir(parents=True, exist_ok=True)
    ctx = context or {}
    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        result = process_file(path, dest, rel, context=ctx, overwrite=overwrite)
        if result is not None:
            written.append(result)
    return written


def load_layer(
    source: ResolvedSource,
    root: Path,
    dest: Path,
    *,
    overwrite: bool = True,
    context: dict[str, Any] | None = None,
) -> list[Path]:
    """Load one template/extension layer into dest."""
    template_root = get_template_dir_path(source, root)
    return copy_tree(template_root, dest, overwrite=overwrite, context=context)


def merge_layers(
    layers: list[tuple[ResolvedSource, Path]],
    dest: Path,
    *,
    context: dict[str, Any] | None = None,
) -> list[Path]:
    """Apply layers in order: template → addons → extend (later wins for copies)."""
    written: list[Path] = []
    for source, root in layers:
        written.extend(load_layer(source, root, dest, overwrite=True, context=context))
    return written
