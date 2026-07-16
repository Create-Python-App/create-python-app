"""Local template/extension cache management (CNA cache.ts parity)."""

from __future__ import annotations

import contextlib
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from create_python_app_core.git_cache import (
    CacheMeta,
    read_cache_meta,
    write_cache_meta,
)
from create_python_app_core.paths import default_cache_dir

from create_awesome_python_app.catalog import catalog_url


@dataclass
class CacheEntry:
    id: str
    path: Path
    url: str | None = None
    ref: str | None = None
    fetched_at: float | None = None
    commit: str | None = None
    size_bytes: int = 0
    fsck_ok: bool | None = None


@dataclass
class RemoteTipResult:
    id: str
    behind: bool
    url: str | None = None
    ref: str | None = None
    local_sha: str | None = None
    remote_sha: str | None = None
    error: str | None = None


@dataclass
class DoctorResult:
    check: str
    ok: bool
    detail: str = ""


@dataclass
class CleanResult:
    removed: list[str]
    not_found: list[str]


def repos_root(cache_root: Path | None = None) -> Path:
    return (cache_root or default_cache_dir()) / "repos"


def _dir_size(path: Path) -> int:
    total = 0
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            for child in current.iterdir():
                if child.is_dir():
                    stack.append(child)
                elif child.is_file():
                    with contextlib.suppress(OSError):
                        total += child.stat().st_size
        except OSError:
            continue
    return total


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    timeout: float | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_git_fsck(entry_path: Path) -> bool:
    try:
        _run_git(["fsck", "--no-progress"], cwd=entry_path, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def list_cache_entries(cache_root: Path | None = None) -> list[CacheEntry]:
    root = repos_root(cache_root)
    if not root.is_dir():
        return []
    out: list[CacheEntry] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        meta = read_cache_meta(child)
        out.append(
            CacheEntry(
                id=child.name,
                path=child,
                url=meta.url if meta else None,
                ref=meta.ref if meta else None,
                fetched_at=meta.fetched_at if meta else None,
                commit=meta.commit if meta else None,
                size_bytes=_dir_size(child),
            )
        )
    return out


def clean_cache(
    entry_id: str | None = None,
    *,
    cache_root: Path | None = None,
    catalog: bool = False,
) -> CleanResult:
    root = cache_root or default_cache_dir()
    removed: list[str] = []
    not_found: list[str] = []

    if catalog:
        target = root / "catalog" / "templates.json"
        if target.is_file():
            target.unlink()
            removed.append(str(target))
        catalog_dir = root / "catalog"
        if catalog_dir.is_dir() and not any(catalog_dir.iterdir()):
            catalog_dir.rmdir()
        return CleanResult(removed=removed, not_found=not_found)

    repos = root / "repos"
    if entry_id:
        target = repos / entry_id
        if not target.exists():
            return CleanResult(removed=[], not_found=[entry_id])
        shutil.rmtree(target)
        return CleanResult(removed=[str(target)], not_found=[])

    if not repos.is_dir():
        return CleanResult(removed=[], not_found=[])

    for child in list(repos.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
            removed.append(str(child))
    return CleanResult(removed=removed, not_found=[])


def verify_cache(
    entry_id: str | None = None,
    *,
    cache_root: Path | None = None,
) -> list[CacheEntry]:
    entries = list_cache_entries(cache_root)
    if entry_id:
        entries = [e for e in entries if e.id == entry_id]
    for entry in entries:
        entry.fsck_ok = run_git_fsck(entry.path)
    return entries


def _remote_tip_sha(git_url: str, ref: str) -> str | None:
    try:
        result = _run_git(
            ["ls-remote", git_url, ref],
            check=True,
            timeout=15,
        )
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        OSError,
        subprocess.TimeoutExpired,
    ):
        return None
    first = result.stdout.strip().splitlines()
    if not first:
        return None
    return first[0].split()[0]


def check_outdated(cache_root: Path | None = None) -> list[RemoteTipResult]:
    results: list[RemoteTipResult] = []
    for entry in list_cache_entries(cache_root):
        if not entry.url or not entry.ref:
            results.append(
                RemoteTipResult(
                    id=entry.id,
                    behind=False,
                    url=entry.url,
                    ref=entry.ref,
                    error="no remote URL in meta"
                    if not entry.url
                    else "no branch/ref in meta",
                )
            )
            continue
        remote_sha = _remote_tip_sha(entry.url, entry.ref)
        if not remote_sha:
            results.append(
                RemoteTipResult(
                    id=entry.id,
                    behind=False,
                    url=entry.url,
                    ref=entry.ref,
                    local_sha=entry.commit,
                    error="unable to fetch remote tip",
                )
            )
            continue
        behind = bool(entry.commit and remote_sha != entry.commit)
        results.append(
            RemoteTipResult(
                id=entry.id,
                behind=behind,
                url=entry.url,
                ref=entry.ref,
                local_sha=entry.commit,
                remote_sha=remote_sha,
            )
        )
    return results


def update_cache(
    entry_id: str | None = None,
    *,
    cache_root: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Fetch/merge cached repos. Returns (updated_ids, failed_ids)."""
    entries = list_cache_entries(cache_root)
    targets = [e for e in entries if e.id == entry_id] if entry_id else entries
    updated: list[str] = []
    failed: list[str] = []
    for entry in targets:
        if not entry.url:
            failed.append(entry.id)
            continue
        try:
            _run_git(["fetch", "--all", "--tags"], cwd=entry.path, check=True)
            ref = entry.ref
            if ref:
                branch_ref = ref if ref.startswith("refs/") else f"origin/{ref}"
                try:
                    _run_git(
                        ["merge", "--ff-only", branch_ref],
                        cwd=entry.path,
                        check=True,
                    )
                except subprocess.CalledProcessError:
                    _run_git(["checkout", ref], cwd=entry.path, check=True)
            commit = _run_git(
                ["rev-parse", "HEAD"], cwd=entry.path, check=True
            ).stdout.strip()
            write_cache_meta(
                entry.path,
                CacheMeta(
                    url=entry.url,
                    ref=entry.ref,
                    fetched_at=time.time(),
                    commit=commit,
                ),
            )
            updated.append(entry.id)
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            failed.append(entry.id)
    return updated, failed


def _probe_network() -> DoctorResult:
    url = catalog_url()
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            status = getattr(resp, "status", 200)
            if 200 <= int(status) < 400:
                return DoctorResult(
                    check="network",
                    ok=True,
                    detail=f"catalog reachable ({url})",
                )
            return DoctorResult(
                check="network",
                ok=False,
                detail=f"HTTP {status} for {url}",
            )
    except urllib.error.HTTPError as exc:
        # Some hosts reject HEAD; treat 4xx/405 as reachable enough for doctor.
        if exc.code in {403, 404, 405}:
            return DoctorResult(
                check="network",
                ok=True,
                detail=f"catalog host reachable ({url})",
            )
        return DoctorResult(check="network", ok=False, detail=str(exc))
    except Exception as exc:  # noqa: BLE001 — doctor surfaces any probe failure
        return DoctorResult(check="network", ok=False, detail=str(exc))


def run_doctor(cache_root: Path | None = None) -> list[DoctorResult]:
    results: list[DoctorResult] = []
    root = cache_root or default_cache_dir()

    try:
        ver = _run_git(["--version"], check=True).stdout.strip()
        results.append(DoctorResult(check="git", ok=True, detail=ver))
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        results.append(
            DoctorResult(check="git", ok=False, detail=f"git not found on PATH ({exc})")
        )

    results.append(_probe_network())

    try:
        root.mkdir(parents=True, exist_ok=True)
        probe = root / ".doctor-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        results.append(DoctorResult(check="cache-dir", ok=True, detail=str(root)))
    except OSError as exc:
        results.append(DoctorResult(check="cache-dir", ok=False, detail=str(exc)))

    entries = list_cache_entries(root)
    corrupt = [e for e in entries if not run_git_fsck(e.path)]
    if not corrupt:
        results.append(
            DoctorResult(
                check="cache-integrity",
                ok=True,
                detail=f"{len(entries)} entries, all clean",
            )
        )
    else:
        ids = ", ".join(e.id for e in corrupt)
        results.append(
            DoctorResult(
                check="cache-integrity",
                ok=False,
                detail=f"{len(corrupt)}/{len(entries)} entries failed git fsck: {ids}",
            )
        )
    return results


def format_bytes(num: int) -> str:
    if num < 1024:
        return f"{num} B"
    if num < 1024 * 1024:
        return f"{num / 1024:.1f} KB"
    if num < 1024 * 1024 * 1024:
        return f"{num / (1024 * 1024):.1f} MB"
    return f"{num / (1024 * 1024 * 1024):.2f} GB"


def format_age(fetched_at: float | None) -> str:
    if fetched_at is None:
        return "—"
    minutes = int((time.time() - fetched_at) / 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def short_sha(sha: str | None) -> str:
    if not sha:
        return "—"
    return sha[:7]


def entry_as_dict(entry: CacheEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "path": str(entry.path),
        "url": entry.url,
        "ref": entry.ref,
        "fetched_at": entry.fetched_at,
        "commit": entry.commit,
        "size_bytes": entry.size_bytes,
        "fsck_ok": entry.fsck_ok,
    }
