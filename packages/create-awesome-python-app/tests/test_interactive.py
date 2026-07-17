import json
import os
from pathlib import Path

from create_awesome_python_app.cli import _in_ci, app
from typer.testing import CliRunner

runner = CliRunner()


class FakePrompt:
    def __init__(self, answer):
        self.answer = answer

    def ask(self):
        return self.answer


async def fake_check_for_latest_version(_package_name):
    return None


def test_in_ci_env(monkeypatch) -> None:
    monkeypatch.setenv("CI", "true")
    assert _in_ci() is True
    monkeypatch.delenv("CI", raising=False)
    # may still be true in this environment; function checks CI only
    os.environ.pop("CI", None)


def test_interactive_template_autocomplete_omits_pointer(
    tmp_path: Path, monkeypatch
) -> None:
    """questionary.autocomplete rejects ``pointer`` (PromptSession TypeError)."""
    template_dir = tmp_path / "fastapi"
    template_dir.mkdir()
    (template_dir / "cpa.config.json").write_text(
        json.dumps({"name": "fastapi-starter"}),
        encoding="utf-8",
    )
    catalog = {
        "categories": [{"slug": "backend-applications", "name": "Backend"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": f"file://{template_dir}",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")
    monkeypatch.delenv("CI", raising=False)

    captured_kwargs: dict[str, object] = {}

    def fake_autocomplete(*_args, **kwargs):
        captured_kwargs.update(kwargs)
        return FakePrompt("Backend     FastAPI Starter (fastapi-starter)")

    def fake_checkbox(*_args, **_kwargs):
        return FakePrompt([])

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr("questionary.autocomplete", fake_autocomplete)
    monkeypatch.setattr("questionary.checkbox", fake_checkbox)
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )

    result = runner.invoke(app, ["--interactive", "--no-install", "api"])

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "pointer" not in captured_kwargs
    assert captured["project_directory"] == "api"


def test_interactive_extension_selection_passes_addon_urls(
    tmp_path: Path, monkeypatch
) -> None:
    template_dir = tmp_path / "fastapi"
    template_dir.mkdir()
    (template_dir / "cpa.config.json").write_text(
        json.dumps({"name": "fastapi-starter"}),
        encoding="utf-8",
    )
    catalog = {
        "categories": [{"slug": "tooling", "name": "Tooling"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": f"file://{template_dir}",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [
            {
                "slug": "github-setup",
                "name": "GitHub Setup",
                "url": "file:///extensions/github",
                "type": ["fastapi-backend"],
                "category": "tooling",
            }
        ],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    answers = [["tooling"], ["file:///extensions/github"]]

    def fake_checkbox(*_args, **_kwargs):
        return FakePrompt(answers.pop(0))

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr("questionary.checkbox", fake_checkbox)
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            "fastapi-starter",
            "--interactive",
            "--no-install",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert captured["project_directory"] == "api"
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["addons"] == ["file:///extensions/github"]


def test_interactive_custom_options_pass_set_values(
    tmp_path: Path, monkeypatch
) -> None:
    template_dir = tmp_path / "fastapi"
    template_dir.mkdir()
    (template_dir / "cpa.config.json").write_text(
        json.dumps(
            {
                "name": "fastapi-starter",
                "customOptions": [
                    {
                        "key": "apiPrefix",
                        "type": "string",
                        "message": "API prefix",
                        "default": "/api/v1",
                    },
                    {
                        "key": "enableCors",
                        "type": "boolean",
                        "message": "Enable CORS",
                        "default": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    catalog = {
        "categories": [{"slug": "backend-applications", "name": "Backend"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": f"file://{template_dir}",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    text_answers = ["/api/v2"]

    def fake_text(*_args, **_kwargs):
        return FakePrompt(text_answers.pop(0))

    def fake_confirm(*_args, **_kwargs):
        return FakePrompt(False)

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr("questionary.text", fake_text)
    monkeypatch.setattr("questionary.confirm", fake_confirm)
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            "fastapi-starter",
            "--interactive",
            "--no-install",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["set"] == {
        "apiPrefix": "/api/v2",
        "enableCors": "false",
    }


def test_interactive_custom_options_honor_set_override(
    tmp_path: Path, monkeypatch
) -> None:
    template_dir = tmp_path / "fastapi"
    template_dir.mkdir()
    (template_dir / "cpa.config.json").write_text(
        json.dumps(
            {
                "name": "fastapi-starter",
                "customOptions": [
                    {
                        "key": "apiPrefix",
                        "type": "string",
                        "message": "API prefix",
                        "default": "/api/v1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    catalog = {
        "categories": [{"slug": "backend-applications", "name": "Backend"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": f"file://{template_dir}",
                "type": "fastapi-backend",
                "category": "backend-applications",
            }
        ],
        "extensions": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    def fail_text(*_args, **_kwargs):
        raise AssertionError("--set options should not be prompted")

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr("questionary.text", fail_text)
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            "fastapi-starter",
            "--interactive",
            "--set",
            "apiPrefix=/forced",
            "--no-install",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["set"] == {"apiPrefix": "/forced"}


def test_interactive_custom_options_fallback_to_registry(
    tmp_path: Path, monkeypatch
) -> None:
    template_dir = tmp_path / "fastapi"
    template_dir.mkdir()
    (template_dir / "cpa.config.json").write_text(
        json.dumps({"name": "fastapi-starter"}),
        encoding="utf-8",
    )
    catalog = {
        "categories": [{"slug": "backend-applications", "name": "Backend"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": f"file://{template_dir}",
                "type": "fastapi-backend",
                "category": "backend-applications",
                "customOptions": [
                    {
                        "name": "apiPrefix",
                        "type": "string",
                        "message": "API prefix",
                        "initial": "/api/v1",
                    }
                ],
            }
        ],
        "extensions": [],
    }
    catalog_file = tmp_path / "templates.json"
    catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setenv("CPA_CATALOG_URL", f"file://{catalog_file}")
    monkeypatch.setenv("CPA_NO_CATALOG_CACHE", "1")

    def fake_text(*_args, **_kwargs):
        return FakePrompt("/api/v3")

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    monkeypatch.setattr("questionary.text", fake_text)
    monkeypatch.setattr(
        "create_awesome_python_app.cli.create_python_app",
        fake_create_python_app,
    )
    monkeypatch.setattr(
        "create_awesome_python_app.cli.check_for_latest_version",
        fake_check_for_latest_version,
    )

    result = runner.invoke(
        app,
        [
            "--template",
            "fastapi-starter",
            "--interactive",
            "--no-install",
            "api",
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    options = captured["options"]
    assert isinstance(options, dict)
    assert options["set"] == {"apiPrefix": "/api/v3"}
