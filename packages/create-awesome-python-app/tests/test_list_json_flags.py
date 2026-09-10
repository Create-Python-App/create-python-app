"""Tests for list/config/install CLI flags (#262, #263, #268, #271, #273)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(autouse=True)
def _fixture_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the offline fixture catalog at this checkout's fixtures/."""
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    monkeypatch.setenv("CPA_FIXTURE_DIR", str(REPO_ROOT))


def _json_out(result) -> dict:
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_list_templates_json_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    payload = _json_out(runner.invoke(app, ["--list-templates", "--json"]))
    slugs = [t["slug"] for t in payload["templates"]]
    assert "fastapi-starter" in slugs
    assert "example-cli" in slugs


def test_list_templates_json_pipes_through_jq_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every entry carries the fields scripts need (jq-parseable contract)."""
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    payload = _json_out(runner.invoke(app, ["--list-templates", "--json"]))
    for entry in payload["templates"]:
        assert {"slug", "name", "description", "category", "labels"} <= set(entry)


def test_list_templates_category_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    payload = _json_out(
        runner.invoke(app, ["--list-templates", "--json", "--category", "tooling"])
    )
    assert [t["slug"] for t in payload["templates"]] == ["example-cli"]


def test_list_templates_unknown_category_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    result = runner.invoke(app, ["--list-templates", "--category", "nope"])
    assert result.exit_code == 2
    combined = (result.stdout or "") + (result.stderr or "")
    assert "Unknown category 'nope'" in combined
    assert "Available:" in combined


def test_list_addons_json_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CPA_CATALOG_FIXTURE", "1")
    payload = _json_out(
        runner.invoke(app, ["--template", "fastapi-starter", "--list-addons", "--json"])
    )
    assert isinstance(payload["addons"], list)


def _capture_create(monkeypatch: pytest.MonkeyPatch) -> dict:
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
    return captured


def _scaffold_args(tmp_path: Path, *extra: str) -> list[str]:
    return [
        str(tmp_path / "proj"),
        "--template",
        "fastapi-starter",
        "--no-interactive",
        f"--fixture={REPO_ROOT}",
        "--no-install",
        *extra,
    ]


@pytest.mark.parametrize("flag", ["--no-install", "--skip-install"])
def test_skip_install_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, flag: str
) -> None:
    captured = _capture_create(monkeypatch)
    args = _scaffold_args(tmp_path)
    args[args.index("--no-install")] = flag
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert captured["options"]["install"] is False


def test_skip_install_in_help() -> None:
    result = runner.invoke(app, ["--help"], env={"COLUMNS": "120"})
    assert result.exit_code == 0
    assert "--skip-install" in (result.stdout or "")


def test_set_overrides_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_create(monkeypatch)
    result = runner.invoke(
        app,
        _scaffold_args(tmp_path, "--set", "project_slug=my-app", "--set", "debug=true"),
    )
    assert result.exit_code == 0, result.output
    assert captured["options"]["set"] == {"project_slug": "my-app", "debug": "true"}


def test_set_malformed_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _capture_create(monkeypatch)
    result = runner.invoke(app, _scaffold_args(tmp_path, "--set", "novalue"))
    assert result.exit_code == 2
    assert "expected key=value" in (result.output or "")


def test_config_file_defaults_merged_under_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_create(monkeypatch)
    cfg = tmp_path / "cpa.config.json"
    cfg.write_text(
        json.dumps({"project_slug": "from-config", "workers": 4, "debug": False}),
        encoding="utf-8",
    )
    result = runner.invoke(
        app, _scaffold_args(tmp_path, "--config", str(cfg), "--set", "debug=true")
    )
    assert result.exit_code == 0, result.output
    # File supplies defaults (scalars stringified); explicit --set wins.
    assert captured["options"]["set"] == {
        "project_slug": "from-config",
        "workers": "4",
        "debug": "true",
    }


def test_config_missing_file_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _capture_create(monkeypatch)
    result = runner.invoke(
        app, _scaffold_args(tmp_path, "--config", str(tmp_path / "missing.json"))
    )
    assert result.exit_code == 2
    assert "--config file not found" in (result.output or "")


def test_config_invalid_json_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _capture_create(monkeypatch)
    cfg = tmp_path / "bad.json"
    cfg.write_text("[1, 2]", encoding="utf-8")
    result = runner.invoke(app, _scaffold_args(tmp_path, "--config", str(cfg)))
    assert result.exit_code == 2
    # Rich wraps long console lines; match the stable tail.
    assert "JSON object" in (result.output or "")
