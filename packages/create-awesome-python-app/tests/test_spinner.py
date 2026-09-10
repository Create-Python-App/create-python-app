"""Tests for the scaffold progress spinner (#269)."""

from __future__ import annotations

import pytest
from create_awesome_python_app.cli import _phase_status, _spinner_enabled


def test_spinner_disabled_without_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stderr.isatty", lambda: True)
    monkeypatch.delenv("CI", raising=False)
    assert _spinner_enabled(interactive=False) is False


def test_spinner_disabled_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stderr.isatty", lambda: True)
    monkeypatch.setenv("CI", "1")
    assert _spinner_enabled(interactive=True) is False


def test_spinner_disabled_without_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stderr.isatty", lambda: False)
    monkeypatch.delenv("CI", raising=False)
    assert _spinner_enabled(interactive=True) is False


def test_spinner_enabled_on_interactive_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stderr.isatty", lambda: True)
    monkeypatch.delenv("CI", raising=False)
    assert _spinner_enabled(interactive=True) is True


def test_phase_status_noop_when_disabled() -> None:
    with _phase_status("Working…", enabled=False):
        pass
