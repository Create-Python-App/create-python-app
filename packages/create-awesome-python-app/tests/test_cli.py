import os
from pathlib import Path

import pytest
from create_awesome_python_app import __version__
from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    combined = result.stdout + result.stderr
    assert __version__ in combined


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


def test_incompatible_addons_fail_fast(tmp_path: Path, monkeypatch) -> None:
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    catalog = {
        "templates": [
            {"slug": "fastapi-starter", "url": f"file://{tpl}"},
        ],
        "extensions": [
            {
                "slug": "saga",
                "url": "file:///ext/saga",
                "incompatibleWith": ["thunk"],
            },
            {
                "slug": "thunk",
                "url": "file:///ext/thunk",
                "incompatibleWith": ["saga"],
            },
        ],
    }

    async def fake_check_for_latest_version(_package_name):
        return None

    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.catalog.get_catalog_data",
        lambda: catalog,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            "fastapi-starter",
            "--addons",
            "saga",
            "--addons",
            "thunk",
            "--no-install",
            "--no-interactive",
            "api",
        ],
    )

    text = (result.stdout or "") + (result.stderr or "")
    assert result.exit_code == 2
    assert "Incompatible extension combination" in text
    assert "saga" in text


def test_help_mentions_fixture() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    text = (result.stdout or "") + (result.stderr or "")
    assert "fixture" in text.lower()


def test_options_after_project_directory(tmp_path: Path, monkeypatch) -> None:
    """Regression: README-style `cpa my-api --template …` must work.

    Registering a Typer subcommand group made Click treat ``--template`` as a
    COMMAND after the positional project directory.
    """
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
            "my-api",
            "--template",
            f"file://{tpl}",
            "--addons",
            "github-setup",
            "--no-install",
            "--no-interactive",
        ],
    )

    text = (result.stdout or "") + (result.stderr or "")
    assert result.exit_code == 0, text
    assert "No such command" not in text
    assert captured["project_directory"] == "my-api"
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["template"] == f"file://{tpl}"


def test_expand_variadic_addons_and_extend() -> None:
    from create_awesome_python_app.cli import (
        _expand_variadic_option,
        _preprocess_cli_argv,
    )

    assert _expand_variadic_option(
        ["cpa", "my-api", "--addons", "fastapi-docker", "github-setup", "--no-install"],
        "--addons",
    ) == [
        "cpa",
        "my-api",
        "--addons",
        "fastapi-docker",
        "--addons",
        "github-setup",
        "--no-install",
    ]
    assert _preprocess_cli_argv(
        [
            "cpa",
            "my-api",
            "--template",
            "fastapi-starter",
            "--addons",
            "fastapi-docker",
            "github-setup",
            "--extend",
            "a",
            "b",
            "--no-interactive",
        ]
    ) == [
        "cpa",
        "my-api",
        "--template",
        "fastapi-starter",
        "--addons",
        "fastapi-docker",
        "--addons",
        "github-setup",
        "--extend",
        "a",
        "--extend",
        "b",
        "--no-interactive",
    ]


def test_space_separated_addons_after_project_directory(
    tmp_path: Path, monkeypatch
) -> None:
    """CNA parity: ``--addons fastapi-docker github-setup`` (one flag, many values)."""
    from create_awesome_python_app.cli import _preprocess_cli_argv

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

    argv = _preprocess_cli_argv(
        [
            "cpa",
            "my-api",
            "--template",
            f"file://{tpl}",
            "--addons",
            "fastapi-docker",
            "github-setup",
            "--no-install",
            "--no-interactive",
        ]
    )
    result = runner.invoke(app, argv[1:])

    text = (result.stdout or "") + (result.stderr or "")
    assert result.exit_code == 0, text
    assert "unexpected extra argument" not in text.lower()
    options = captured["options"]
    assert isinstance(options, dict)
    addons = options["addons"]
    assert isinstance(addons, list)
    assert len(addons) == 2
    assert any("fastapi-docker" in a for a in addons)
    assert any("github-setup" in a for a in addons)


def test_preprocess_fixture_argv_bare_and_with_dir() -> None:
    from create_awesome_python_app.cli import _FIXTURE_AUTO, _preprocess_fixture_argv

    assert _preprocess_fixture_argv(["cpa", "--fixture", "--list-templates"]) == [
        "cpa",
        f"--fixture={_FIXTURE_AUTO}",
        "--list-templates",
    ]
    assert _preprocess_fixture_argv(
        ["cpa", "--fixture", "./my-fixtures", "--list-templates"]
    ) == ["cpa", "--fixture", "./my-fixtures", "--list-templates"]


def test_fixture_flag_enables_catalog_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from create_awesome_python_app.cli import _FIXTURE_AUTO, apply_fixture_mode

    apply_fixture_mode(_FIXTURE_AUTO)
    assert os.environ.get("CPA_CATALOG_FIXTURE") == "1"
    assert "CPA_FIXTURE_DIR" not in os.environ

    monkeypatch.delenv("CPA_CATALOG_FIXTURE", raising=False)
    monkeypatch.delenv("CPA_FIXTURE_DIR", raising=False)
    apply_fixture_mode(str(tmp_path))
    assert os.environ.get("CPA_CATALOG_FIXTURE") == "1"
    assert os.environ.get("CPA_FIXTURE_DIR") == str(tmp_path)


def test_list_templates_with_fixture_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json
    import os

    catalog_dir = tmp_path / "fixtures" / "catalog"
    catalog_dir.mkdir(parents=True)
    (catalog_dir / "templates.json").write_text(
        json.dumps(
            {
                "templates": [
                    {
                        "slug": "fixture-only",
                        "category": "tooling",
                        "type": "cli",
                    }
                ],
                "extensions": [],
                "categories": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("CPA_CATALOG_FIXTURE", raising=False)
    monkeypatch.delenv("CPA_FIXTURE_DIR", raising=False)

    result = runner.invoke(
        app,
        ["--fixture", str(tmp_path), "--list-templates"],
    )
    text = (result.stdout or "") + (result.stderr or "")
    assert result.exit_code == 0, text
    assert "fixture-only" in text
    assert os.environ.get("CPA_CATALOG_FIXTURE") == "1"
