from typer.testing import CliRunner
from create_awesome_python_app.cli import app
runner = CliRunner()
def test_cache_subcommands() -> None:
    for args in (["cache","list"],["cache","outdated"],["cache","doctor"],["cache","verify"],["cache","update"],["cache","clean","--catalog"]):
        assert runner.invoke(app, args).exit_code == 0, args
