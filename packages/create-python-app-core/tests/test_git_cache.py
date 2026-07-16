import json
import time
from pathlib import Path

import pytest
from create_python_app_core.errors import CpaError
from create_python_app_core.git_cache import (
    CacheMeta,
    download_repository,
    read_cache_meta,
    write_cache_meta,
)
from create_python_app_core.paths import ResolvedSource


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
