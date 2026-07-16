from typer.testing import CliRunner

from create_awesome_python_app.cli import app

runner = CliRunner()


def test_help_lists_scaffold_flags() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for flag in [
        "--template",
        "--addons",
        "--extend",
        "--set",
        "--force",
        "--no-install",
    ]:
        assert flag in result.stdout
