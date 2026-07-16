import os

from create_awesome_python_app.cli import _in_ci


def test_in_ci_env(monkeypatch) -> None:
    monkeypatch.setenv("CI", "true")
    assert _in_ci() is True
    monkeypatch.delenv("CI", raising=False)
    # may still be true in this environment; function checks CI only
    os.environ.pop("CI", None)
