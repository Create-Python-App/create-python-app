from create_awesome_python_app.cli import cache_app
from typer.testing import CliRunner

runner = CliRunner()


def test_cache_subcommands() -> None:
    for args in (
        ["dir"],
        ["list"],
        ["outdated"],
        ["doctor"],
        ["verify"],
        ["update"],
        ["clean", "--catalog"],
    ):
        result = runner.invoke(cache_app, args)
        assert result.exit_code == 0, (args, result.stdout, result.stderr)
