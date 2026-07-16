"""Resolve template/extension locations (GitHub URL, file://, slugs, ?ref=)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from create_python_app_core.errors import CpaError

_GITHUB_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/#?]+)(?P<path>/.*)?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ResolvedSource:
    kind: str  # github | file | slug
    url: str
    ref: str | None = None
    subdir: str | None = None
    local_path: Path | None = None


def default_cache_dir() -> Path:
    override = os.environ.get("CPA_CACHE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".cache" / "cpa"


def _parse_ref(query: dict[str, list[str]]) -> str | None:
    refs = query.get("ref") or query.get("branch") or query.get("tag")
    if not refs:
        return None
    ref = refs[0]
    if os.environ.get("CPA_STRICT_REPRO") == "1" and not re.fullmatch(
        r"[0-9a-f]{40}", ref
    ):
        raise CpaError(
            f"Invalid ref parameter '{ref}' with CPA_STRICT_REPRO=1: "
            "expected a full 40-character commit SHA.",
            code="CPA_STRICT_REPRO",
        )
    return ref


def resolve_source(spec: str, *, cache_dir: Path | None = None) -> ResolvedSource:
    """Resolve a template/extension specifier into a concrete source."""
    _ = cache_dir or default_cache_dir()
    if spec.startswith("file://"):
        parsed = urlparse(spec)
        query = parse_qs(parsed.query)
        path = Path(unquote(parsed.path))
        if parsed.netloc and parsed.netloc != "localhost":
            # file://host/path — uncommon; treat netloc+path
            path = Path(f"/{parsed.netloc}{unquote(parsed.path)}")
        subdir = (query.get("subdir") or [None])[0]
        return ResolvedSource(
            kind="file",
            url=spec,
            ref=_parse_ref(query),
            subdir=subdir,
            local_path=path,
        )

    if "://" in spec or spec.startswith("git@"):
        parsed = urlparse(spec if "://" in spec else f"ssh://{spec}")
        query = parse_qs(parsed.query)
        m = _GITHUB_RE.match(spec.split("?")[0])
        kind = "github" if m else "git"
        subdir = (query.get("subdir") or [None])[0]
        return ResolvedSource(
            kind=kind,
            url=spec.split("?")[0],
            ref=_parse_ref(query),
            subdir=subdir,
        )

    # legacy slug
    return ResolvedSource(kind="slug", url=spec, ref=None, subdir=None)


def get_template_dir_path(source: ResolvedSource, root: Path) -> Path:
    """Prefer template/ subdirectory when present."""
    base = root
    if source.subdir:
        base = root / source.subdir
    candidate = base / "template"
    return candidate if candidate.is_dir() else base
