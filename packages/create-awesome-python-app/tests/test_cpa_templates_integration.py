"""Integration tests against the cpa-templates bank."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_CPA_TEMPLATES = (_REPO_ROOT.parent / "cpa-templates").resolve()
CPA_TEMPLATES_ROOT = Path(
    os.environ.get("CPA_TEMPLATES_ROOT", str(_DEFAULT_CPA_TEMPLATES))
).resolve()
FASTAPI_TEMPLATE = CPA_TEMPLATES_ROOT / "templates" / "fastapi-starter"
GITHUB_SETUP = CPA_TEMPLATES_ROOT / "extensions" / "all-github-setup"


def _cpa_templates_available() -> bool:
    return (FASTAPI_TEMPLATE / "pyproject.toml").is_file()


@pytest.mark.skipif(
    not _cpa_templates_available(),
    reason="cpa-templates checkout not available (set CPA_TEMPLATES_ROOT)",
)
def test_scaffold_fastapi_starter_from_cpa_templates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cpa-cache"))
    dest = tmp_path / "api"
    template_url = f"file://{CPA_TEMPLATES_ROOT}?subdir=templates/fastapi-starter"

    result = subprocess.run(
        [
            "uv",
            "run",
            "create-awesome-python-app",
            "--template",
            template_url,
            "--no-interactive",
            "--no-install",
            str(dest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (dest / "app" / "main.py").is_file()
    assert (dest / "pyproject.toml").is_file()

    sync = subprocess.run(["uv", "sync"], cwd=dest, capture_output=True, text=True)
    assert sync.returncode == 0, sync.stderr

    lint = subprocess.run(
        ["uv", "run", "ruff", "check", "."], cwd=dest, capture_output=True, text=True
    )
    assert lint.returncode == 0, lint.stderr

    tests = subprocess.run(
        ["uv", "run", "pytest", "-q"], cwd=dest, capture_output=True, text=True
    )
    assert tests.returncode == 0, tests.stdout + tests.stderr


@pytest.mark.skipif(
    not _cpa_templates_available(),
    reason="cpa-templates checkout not available (set CPA_TEMPLATES_ROOT)",
)
def test_scaffold_fastapi_starter_via_catalog_slug(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scaffold using --template fastapi-starter slug (issue #160 / #161)."""
    import json

    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cpa-cache"))
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cpa-cache"))
    catalog = {
        "templates": [
            {
                "slug": "fastapi-starter",
                "url": (
                    f"file://{CPA_TEMPLATES_ROOT}?subdir=templates/fastapi-starter"
                ),
            }
        ],
        "extensions": [],
        "categories": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    dest = tmp_path / "api-slug"
    result = subprocess.run(
        [
            "uv",
            "run",
            "create-awesome-python-app",
            "--template",
            "fastapi-starter",
            "--no-interactive",
            "--no-install",
            str(dest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (dest / "app" / "main.py").is_file()


@pytest.mark.skipif(
    not (_cpa_templates_available() and GITHUB_SETUP.is_dir()),
    reason="cpa-templates extensions not available",
)
def test_scaffold_via_catalog_addon_slug(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json

    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cpa-cache"))
    repo = CPA_TEMPLATES_ROOT
    catalog = {
        "templates": [
            {
                "slug": "fastapi-starter",
                "url": f"file://{repo}?subdir=templates/fastapi-starter",
            }
        ],
        "extensions": [
            {
                "slug": "github-setup",
                "url": f"file://{repo}?subdir=extensions/all-github-setup",
            }
        ],
        "categories": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    dest = tmp_path / "api-addon-slug"
    result = subprocess.run(
        [
            "uv",
            "run",
            "create-awesome-python-app",
            "--template",
            "fastapi-starter",
            "--addons",
            "github-setup",
            "--no-interactive",
            "--no-install",
            str(dest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (dest / ".github" / "workflows" / "ci.yml").is_file()


@pytest.mark.skipif(
    not (_cpa_templates_available() and GITHUB_SETUP.is_dir()),
    reason="cpa-templates extensions not available",
)
def test_scaffold_fastapi_with_github_setup_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    monkeypatch.setenv("CPA_CACHE_DIR", str(tmp_path / "cpa-cache"))
    dest = tmp_path / "api-ext"
    repo = CPA_TEMPLATES_ROOT
    result = subprocess.run(
        [
            "uv",
            "run",
            "create-awesome-python-app",
            "--template",
            f"file://{repo}?subdir=templates/fastapi-starter",
            "--addons",
            f"file://{repo}?subdir=extensions/all-github-setup",
            "--no-interactive",
            "--no-install",
            str(dest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (dest / ".github" / "workflows" / "ci.yml").is_file()
