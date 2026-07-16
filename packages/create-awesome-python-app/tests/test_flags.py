import re

from create_awesome_python_app.cli import app
from typer.testing import CliRunner

runner = CliRunner()
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def test_help_lists_scaffold_flags() -> None:
    # Wide COLUMNS avoids Rich truncating option names in CI runners.
    result = runner.invoke(
        app,
        ["--help"],
        env={"COLUMNS": "120", "TERM": "xterm-256color", "NO_COLOR": "1"},
    )
    assert result.exit_code == 0
    text = _ANSI.sub("", result.stdout or "")
    for flag in [
        "--template",
        "--addons",
        "--extend",
        "--set",
        "--force",
        "--no-install",
    ]:
        assert flag in text
