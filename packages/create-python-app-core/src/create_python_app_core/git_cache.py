"""Git download + on-disk cache (~/.cache/cpa) with refresh modes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from create_python_app_core.errors import CpaError
from create_python_app_core.paths import ResolvedSource, default_cache_dir

RefreshMode = Literal["always", "stale", "manual"]


@dataclass
class CacheMeta:
    url: str
    ref: str | None
    fetched_at: float
    commit: str | None = None


def resolve_refresh_mode(explicit: RefreshMode | None = None) -> RefreshMode:
    if explicit:
        return explicit
    env = os.environ.get("CPA_REFRESH", "").lower()
    if env in ("always", "stale", "manual"):
        return env  # type: ignore[return-value]
    return "stale"


def refresh_after_hours() -> float:
    raw = os.environ.get("CPA_REFRESH_AFTER_HOURS", "24")
    try:
        return float(raw)
    except ValueError:
        return 24.0


def _cache_key(source: ResolvedSource) -> str:
    safe = source.url.replace("://", "_").replace("/", "_").replace(":", "_")
    ref = source.ref or "default"
    return f"{safe}__{ref}"


def cache_entry_dir(source: ResolvedSource, cache_root: Path | None = None) -> Path:
    root = cache_root or default_cache_dir()
    return root / "repos" / _cache_key(source)


def meta_path(entry: Path) -> Path:
    return entry / ".cpa-cache.json"


def write_cache_meta(entry: Path, meta: CacheMeta) -> None:
    entry.mkdir(parents=True, exist_ok=True)
    meta_path(entry).write_text(
        json.dumps(asdict(meta), indent=2) + "\n", encoding="utf-8"
    )


def read_cache_meta(entry: Path) -> CacheMeta | None:
    path = meta_path(entry)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return CacheMeta(**data)


def _should_refresh(meta: CacheMeta | None, mode: RefreshMode) -> bool:
    if mode == "always":
        return True
    if mode == "manual":
        return False
    # stale
    if meta is None:
        return True
    age_h = (time.time() - meta.fetched_at) / 3600.0
    return age_h >= refresh_after_hours()


def _run_git(args: list[str], *, cwd: Path | None = None) -> str:
    if os.environ.get("CPA_SKIP_GIT") == "1":
        raise CpaError("Git disabled via CPA_SKIP_GIT=1", code="CPA_SKIP_GIT")
    try:
        out = subprocess.check_output(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return out.strip()
    except subprocess.CalledProcessError as exc:
        raise CpaError(
            f"git {' '.join(args)} failed: {exc.output}", code="CPA_GIT"
        ) from exc
    except FileNotFoundError as exc:
        raise CpaError("git executable not found", code="CPA_GIT") from exc


def _remote_default_ref(entry: Path) -> str:
    """Resolve origin/HEAD (e.g. origin/main) for an existing cache clone."""
    try:
        sym = _run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=entry)
        if sym.startswith("refs/remotes/"):
            return sym.removeprefix("refs/remotes/")
        if sym.startswith("origin/"):
            return sym
    except CpaError:
        pass
    for candidate in ("origin/main", "origin/master"):
        try:
            _run_git(["rev-parse", "--verify", candidate], cwd=entry)
            return candidate
        except CpaError:
            continue
    raise CpaError(
        "unable to resolve remote default branch for cache refresh",
        code="CPA_GIT",
    )


def _refresh_cached_repo(entry: Path, ref: str | None) -> str:
    """Fetch and hard-reset the cache clone to the remote tip (CNA pull parity)."""
    _run_git(["fetch", "--all", "--tags"], cwd=entry)
    if ref:
        remote = ref if ref.startswith(("refs/", "origin/")) else f"origin/{ref}"
        local_branch = ref.rsplit("/", 1)[-1]
        _run_git(["checkout", "--force", "-B", local_branch, remote], cwd=entry)
        _run_git(["reset", "--hard", remote], cwd=entry)
    else:
        remote = _remote_default_ref(entry)
        local_branch = remote.rsplit("/", 1)[-1]
        _run_git(["checkout", "--force", "-B", local_branch, remote], cwd=entry)
        _run_git(["reset", "--hard", remote], cwd=entry)
    return _run_git(["rev-parse", "HEAD"], cwd=entry)


def _subdir_missing(entry: Path, source: ResolvedSource) -> bool:
    if not source.subdir:
        return False
    return not (entry / source.subdir).is_dir()


def download_repository(
    source: ResolvedSource,
    *,
    offline: bool = False,
    refresh: RefreshMode | None = None,
    cache_root: Path | None = None,
) -> Path:
    """Clone or refresh a repo into the cache; return the entry directory."""
    if source.kind == "file":
        if source.local_path is None or not source.local_path.exists():
            raise CpaError(f"file source not found: {source.url}", code="CPA_FILE")
        return source.local_path

    entry = cache_entry_dir(source, cache_root)
    mode = resolve_refresh_mode(refresh)
    meta = read_cache_meta(entry)

    if offline:
        if not entry.exists():
            raise CpaError(
                f"offline mode: cache miss for {source.url}",
                code="CPA_OFFLINE",
            )
        return entry

    needs_refresh = _should_refresh(meta, mode) or (
        entry.exists() and _subdir_missing(entry, source)
    )
    if entry.exists() and not needs_refresh:
        return entry

    if entry.exists() and (entry / ".git").is_dir() and mode != "manual":
        commit = _refresh_cached_repo(entry, source.ref)
    else:
        if entry.exists():
            shutil.rmtree(entry)
        entry.mkdir(parents=True, exist_ok=True)
        clone_args = ["clone", "--depth", "1"]
        if source.ref:
            clone_args.extend(["--branch", source.ref])
        clone_args.extend([source.url, str(entry)])
        _run_git(clone_args)
        commit = _run_git(["rev-parse", "HEAD"], cwd=entry)

    write_cache_meta(
        entry,
        CacheMeta(
            url=source.url, ref=source.ref, fetched_at=time.time(), commit=commit
        ),
    )
    return entry
