import os
from pathlib import Path

import pytest
from create_python_app_core.errors import CpaError
from create_python_app_core.paths import default_cache_dir, resolve_source


def test_default_cache_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CPA_CACHE_DIR", raising=False)
    assert default_cache_dir() == Path.home() / ".cache" / "cpa"
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "c"))
    assert default_cache_dir() == (tmp_path / "c").resolve()


def test_file_url(tmp_path: Path) -> None:
    src = resolve_source(f"file://{tmp_path}?subdir=templates/foo")
    assert src.kind == "file"
    assert src.subdir == "templates/foo"


def test_windows_drive_letter_file_url() -> None:
    if os.name != "nt":
        pytest.skip("Windows path handling is only relevant on Windows")

    src = resolve_source("file:///E:/create-python/cpa-templates?subdir=templates/foo")
    assert src.kind == "file"
    assert src.subdir == "templates/foo"
    assert src.local_path == Path(r"E:\create-python\cpa-templates")


def test_github_url_with_ref() -> None:
    src = resolve_source("https://github.com/org/repo?ref=main&subdir=templates/x")
    assert src.kind == "github"
    assert src.ref == "main"
    assert src.subdir == "templates/x"


def test_strict_repro_requires_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CPA_STRICT_REPRO", "1")
    with pytest.raises(CpaError):
        resolve_source("https://github.com/org/repo?ref=main")
    sha = "a" * 40
    src = resolve_source(f"https://github.com/org/repo?ref={sha}")
    assert src.ref == sha


def test_slug() -> None:
    assert resolve_source("fastapi-starter").kind == "slug"
