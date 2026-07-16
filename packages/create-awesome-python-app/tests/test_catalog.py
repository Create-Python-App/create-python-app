from typer.testing import CliRunner
from create_awesome_python_app.cli import app
runner = CliRunner()
def test_list_templates() -> None:
    r = runner.invoke(app, [\"--list-templates\"])
    assert r.exit_code == 0
def test_list_addons() -> None:
    assert runner.invoke(app, [\"--list-addons\"]).exit_code == 0
