from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    combined = result.stdout + result.stderr
    assert "0.1.0" in combined


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scaffold" in result.stdout or "create" in result.stdout.lower()
