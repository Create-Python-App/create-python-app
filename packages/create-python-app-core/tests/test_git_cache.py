import json
import subprocess
import time
from pathlib import Path

import pytest
from create_python_app_core.errors import CpaError
from create_python_app_core.git_cache import (
    CacheMeta,
    download_repository,
    write_cache_meta,
)
from create_python_app_core.paths import ResolvedSource


def _git(args: list[str], *, cwd: Path) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=cwd, text=True, stderr=subprocess.STDOUT
    ).strip()


def _init_remote(path: Path) -> None:
    path.mkdir(parents=True)
    _git(["init", "-b", "main"], cwd=path)
    _git(["config", "user.email", "test@example.com"], cwd=path)
    _git(["config", "user.name", "Test"], cwd=path)
    (path / "README.md").write_text("v1\n", encoding="utf-8")
    (path / "extensions" / "legacy").mkdir(parents=True)
    (path / "extensions" / "legacy" / "ok.txt").write_text("legacy\n", encoding="utf-8")
    _git(["add", "."], cwd=path)
    _git(["commit", "-m", "init"], cwd=path)


def test_file_source_returns_path(tmp_path: Path) -> None:
    src = ResolvedSource(kind="file", url=f"file://{tmp_path}", local_path=tmp_path)
    assert download_repository(src) == tmp_path


def test_offline_miss_raises(tmp_path: Path) -> None:
    src = ResolvedSource(kind="github", url="https://github.com/org/repo")
    with pytest.raises(CpaError) as ei:
        download_repository(src, offline=True, cache_root=tmp_path)
    assert ei.value.code == "CPA_OFFLINE"


def test_meta_roundtrip(tmp_path: Path) -> None:
    entry = tmp_path / "e"
    meta = CacheMeta(url="u", ref="main", fetched_at=time.time(), commit="abc")
    write_cache_meta(entry, meta)
    from create_python_app_core.git_cache import read_cache_meta

    loaded = read_cache_meta(entry)
    assert loaded is not None
    assert loaded.url == "u"
    assert json.loads((entry / ".cpa-cache.json").read_text())["ref"] == "main"


def test_skip_git_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    src = ResolvedSource(kind="github", url="https://github.com/org/repo")
    with pytest.raises(CpaError) as ei:
        download_repository(src, cache_root=tmp_path, refresh="always")
    assert ei.value.code == "CPA_SKIP_GIT"


def test_refresh_without_ref_advances_to_remote_tip(tmp_path: Path) -> None:
    work = tmp_path / "work"
    bare = tmp_path / "bare.git"
    cache = tmp_path / "cache"

    _init_remote(work)
    _git(["clone", "--bare", str(work), str(bare)], cwd=tmp_path)

    src = ResolvedSource(kind="git", url=str(bare))
    first = download_repository(src, cache_root=cache, refresh="always")
    first_sha = _git(["rev-parse", "HEAD"], cwd=first)
    assert (first / "extensions" / "legacy" / "ok.txt").is_file()
    assert not (first / "extensions" / "all-github-setup").exists()

    _git(["clone", str(bare), str(tmp_path / "push")], cwd=tmp_path)
    push = tmp_path / "push"
    _git(["config", "user.email", "test@example.com"], cwd=push)
    _git(["config", "user.name", "Test"], cwd=push)
    (push / "extensions" / "all-github-setup").mkdir(parents=True)
    (push / "extensions" / "all-github-setup" / "ok.txt").write_text(
        "new\n", encoding="utf-8"
    )
    _git(["add", "."], cwd=push)
    _git(["commit", "-m", "rename extension"], cwd=push)
    _git(["push", "origin", "main"], cwd=push)
    new_sha = _git(["rev-parse", "HEAD"], cwd=push)
    assert new_sha != first_sha

    refreshed = download_repository(src, cache_root=cache, refresh="always")
    assert refreshed == first
    assert _git(["rev-parse", "HEAD"], cwd=refreshed) == new_sha
    assert (refreshed / "extensions" / "all-github-setup" / "ok.txt").is_file()


def test_missing_subdir_forces_refresh_when_meta_is_fresh(tmp_path: Path) -> None:
    work = tmp_path / "work"
    bare = tmp_path / "bare.git"
    cache = tmp_path / "cache"
    _init_remote(work)
    _git(["clone", "--bare", str(work), str(bare)], cwd=tmp_path)

    src = ResolvedSource(
        kind="git",
        url=str(bare),
        subdir="extensions/all-github-setup",
    )
    entry = download_repository(src, cache_root=cache, refresh="always")
    write_cache_meta(
        entry,
        CacheMeta(
            url=str(bare),
            ref=None,
            fetched_at=time.time(),
            commit=_git(["rev-parse", "HEAD"], cwd=entry),
        ),
    )
    assert not (entry / "extensions" / "all-github-setup").exists()

    _git(["clone", str(bare), str(tmp_path / "push")], cwd=tmp_path)
    push = tmp_path / "push"
    _git(["config", "user.email", "test@example.com"], cwd=push)
    _git(["config", "user.name", "Test"], cwd=push)
    (push / "extensions" / "all-github-setup").mkdir(parents=True)
    (push / "extensions" / "all-github-setup" / "ok.txt").write_text(
        "new\n", encoding="utf-8"
    )
    _git(["add", "."], cwd=push)
    _git(["commit", "-m", "add all-github-setup"], cwd=push)
    _git(["push", "origin", "main"], cwd=push)

    updated = download_repository(src, cache_root=cache, refresh="stale")
    assert (updated / "extensions" / "all-github-setup" / "ok.txt").is_file()
