import json
import os
from pathlib import Path

from create_awesome_python_app.cli import _in_ci, app
from typer.testing import CliRunner

runner = CliRunner()


def test_in_ci_env(monkeypatch) -> None:
    monkeypatch.setenv("CI", "true")
    assert _in_ci() is True
    monkeypatch.delenv("CI", raising=False)
    # may still be true in this environment; function checks CI only
    os.environ.pop("CI", None)


def test_interactive_extension_selection_passes_addon_urls(
    tmp_path: Path, monkeypatch
) -> None:
    catalog = {
        "categories": [{"slug": "tooling", "name": "Tooling"}],
        "templates": [
            {
                "slug": "fastapi-starter",
                "name": "FastAPI Starter",
                "url": "file:///templates/fastapi",
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

    class FakePrompt:
        def __init__(self, answer):
            self.answer = answer

        def ask(self):
            return self.answer

    def fake_checkbox(*_args, **_kwargs):
        return FakePrompt(answers.pop(0))

    captured: dict[str, object] = {}

    async def fake_create_python_app(project_directory, options, *_args, **_kwargs):
        captured["project_directory"] = project_directory
        captured["options"] = options

    async def fake_check_for_latest_version(_package_name):
        return None

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
