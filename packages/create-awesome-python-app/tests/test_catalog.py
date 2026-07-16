from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_list_templates() -> None:
    result = runner.invoke(app, ["--list-templates"])
    assert result.exit_code == 0


def test_list_addons() -> None:
    assert runner.invoke(app, ["--list-addons"]).exit_code == 0
