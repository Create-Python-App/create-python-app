"""Tests for cache verify/outdated/update/doctor (CNA cache parity)."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest
from create_awesome_python_app.cache import (
    check_outdated,
    clean_cache,
    list_cache_entries,
    run_doctor,
    update_cache,
    verify_cache,
)
from create_awesome_python_app.cli import cache_app
from create_python_app_core.git_cache import CacheMeta, write_cache_meta
from typer.testing import CliRunner

runner = CliRunner()


def _out(result) -> str:
    return (result.stdout or "") + (result.stderr or "")


def _init_git_repo(path: Path) -> str:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    (path / "README.md").write_text("hi\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True
    )
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=path, text=True
    ).strip()
    return sha


@pytest.fixture()
def cache_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "cpa-cache"
    root.mkdir()
    monkeypatch.setenv("CPA_CACHE_DIR", str(root))
    return root


def test_cache_subcommands_exit_zero(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "create_awesome_python_app.cache._probe_network",
        lambda: __import__(
            "create_awesome_python_app.cache", fromlist=["DoctorResult"]
        ).DoctorResult(check="network", ok=True, detail="mocked"),
    )
    for args in (
        ["dir"],
        ["list"],
        ["outdated"],
        ["doctor"],
        ["verify"],
        ["update"],
        ["clean", "--catalog"],
    ):
        result = runner.invoke(cache_app, args)
        assert result.exit_code == 0, (args, _out(result))


def test_list_cache_entries_empty(cache_root: Path) -> None:
    assert list_cache_entries() == []


def test_list_and_verify_populated_entry(cache_root: Path) -> None:
    entry = cache_root / "repos" / "demo-entry"
    sha = _init_git_repo(entry)
    write_cache_meta(
        entry,
        CacheMeta(
            url="https://example.com/repo.git",
            ref="main",
            fetched_at=time.time(),
            commit=sha,
        ),
    )
    entries = list_cache_entries()
    assert len(entries) == 1
    assert entries[0].id == "demo-entry"
    assert entries[0].url == "https://example.com/repo.git"
    assert entries[0].commit == sha
    assert entries[0].size_bytes > 0

    verified = verify_cache()
    assert verified[0].fsck_ok is True

    result = runner.invoke(cache_app, ["verify"])
    assert result.exit_code == 0
    assert "demo-entry" in _out(result)


def test_clean_by_id_and_catalog(cache_root: Path) -> None:
    a = cache_root / "repos" / "a"
    b = cache_root / "repos" / "b"
    _init_git_repo(a)
    _init_git_repo(b)
    cat = cache_root / "catalog" / "templates.json"
    cat.parent.mkdir(parents=True)
    cat.write_text("{}", encoding="utf-8")

    result = clean_cache("a")
    assert result.removed == [str(a)]
    assert not a.exists()
    assert b.exists()

    missing = clean_cache("missing")
    assert missing.not_found == ["missing"]

    catalog = clean_cache(catalog=True)
    assert str(cat) in catalog.removed
    assert not cat.exists()


def test_outdated_reports_missing_meta(cache_root: Path) -> None:
    entry = cache_root / "repos" / "bare"
    _init_git_repo(entry)
    results = check_outdated()
    assert len(results) == 1
    assert results[0].error == "no remote URL in meta"


def test_update_without_entries(cache_root: Path) -> None:
    updated, failed = update_cache()
    assert updated == []
    assert failed == []
    result = runner.invoke(cache_app, ["update"])
    assert result.exit_code == 0
    assert "No cached" in _out(result)


def test_doctor_reports_git_and_cache_dir(
    cache_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "create_awesome_python_app.cache._probe_network",
        lambda: __import__(
            "create_awesome_python_app.cache", fromlist=["DoctorResult"]
        ).DoctorResult(check="network", ok=True, detail="mocked"),
    )
    results = run_doctor()
    by_check = {r.check: r for r in results}
    assert by_check["git"].ok
    assert by_check["cache-dir"].ok
    assert by_check["cache-dir"].detail == str(cache_root)
    assert by_check["network"].ok
    assert by_check["cache-integrity"].ok

    result = runner.invoke(cache_app, ["doctor"])
    assert result.exit_code == 0
    text = _out(result)
    assert "git:" in text
    assert "cache-dir:" in text


def test_list_cli_shows_table(cache_root: Path) -> None:
    entry = cache_root / "repos" / "demo"
    sha = _init_git_repo(entry)
    write_cache_meta(
        entry,
        CacheMeta(
            url="https://github.com/Create-Python-App/cpa-templates.git",
            ref="main",
            fetched_at=time.time() - 120,
            commit=sha,
        ),
    )
    result = runner.invoke(cache_app, ["list"])
    assert result.exit_code == 0
    text = _out(result)
    assert "demo" in text
    assert "SHA" in text
