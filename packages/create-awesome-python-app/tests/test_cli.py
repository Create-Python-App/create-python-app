from pathlib import Path

import pytest
from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()
_CPA_ENV_VARS = ("CPA_REFRESH", "CPA_NO_CATALOG_CACHE", "CPA_CACHE_DIR")


@pytest.fixture(autouse=True)
def _clean_cpa_env(monkeypatch):
    for name in _CPA_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    yield
    for name in _CPA_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    combined = result.stdout + result.stderr
    assert "0.1.0" in combined


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scaffold" in result.stdout or "create" in result.stdout.lower()


def test_refresh_flag_is_forwarded(tmp_path: Path, monkeypatch) -> None:
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    captured: dict[str, object] = {}

    async def fake_check_for_latest_version(_package_name):
        return None

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            f"file://{tpl}",
            "--refresh",
            "always",
            "--no-install",
            "--no-interactive",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["refresh"] == "always"


def test_invalid_refresh_mode_fails(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl"
    tpl.mkdir()

    result = runner.invoke(
        app,
        [
            "--template",
            f"file://{tpl}",
            "--refresh",
            "bogus",
            "--no-install",
            "--no-interactive",
            "api",
        ],
    )

    assert result.exit_code == 2
    assert "Invalid --refresh mode" in result.stdout + result.stderr


def test_no_cache_sets_explicit_refresh(tmp_path: Path, monkeypatch) -> None:
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    captured: dict[str, object] = {}

    async def fake_check_for_latest_version(_package_name):
        return None

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            f"file://{tpl}",
            "--no-cache",
            "--no-install",
            "--no-interactive",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["refresh"] == "always"


def test_pin_appends_ref_to_template_url(tmp_path: Path, monkeypatch) -> None:
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    captured: dict[str, object] = {}

    async def fake_check_for_latest_version(_package_name):
        return None

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            f"file://{tpl}",
            "--pin",
            "abc123",
            "--no-install",
            "--no-interactive",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["template"] == f"file://{tpl}?ref=abc123"
