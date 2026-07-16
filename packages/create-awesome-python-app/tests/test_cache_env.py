from typer.testing import CliRunner

from create_awesome_python_app.cli import cache_app

runner = CliRunner()


def test_cache_dir() -> None:
    result = runner.invoke(cache_app, ["dir"])
    assert result.exit_code == 0
