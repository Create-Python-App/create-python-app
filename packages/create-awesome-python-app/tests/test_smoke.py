from pathlib import Path

import pytest
from typer.testing import CliRunner

from create_awesome_python_app.cli import app

runner = CliRunner()


def test_help_smoke() -> None:
    assert runner.invoke(app, ["--help"]).exit_code == 0


def test_scaffold_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    monkeypatch.setenv("CI", "1")
    tpl = tmp_path / "tpl"
    (tpl / "template").mkdir(parents=True)
    (tpl / "template" / "a.txt").write_text("a")
    dest = tmp_path / "app"
    # Options must come before the project_directory argument (Typer parsing).
    result = runner.invoke(
        app,
        [
            "--template",
            f"file://{tpl}",
            "--no-install",
            "--no-interactive",
            str(dest),
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    assert (dest / "a.txt").read_text() == "a"
