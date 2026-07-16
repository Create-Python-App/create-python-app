import asyncio

import pytest
from create_python_app_core import check_python_version, create_python_app


def test_check_python_version_accepts_current() -> None:
    check_python_version(">=3.12", "create-python-app-core")


def test_check_python_version_rejects_impossible() -> None:
    with pytest.raises(SystemExit):
        check_python_version(">=99.0", "create-python-app-core")


def test_create_python_app_forwards_refresh(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_scaffold_project(project_directory: str, **kwargs) -> None:
        captured["project_directory"] = project_directory
        captured.update(kwargs)

    monkeypatch.setattr(
        "create_python_app_core.installer.scaffold_project",
        fake_scaffold_project,
    )

    asyncio.run(
        create_python_app(
            "api",
            {
                "template": "file:///template",
                "install": False,
                "refresh": "always",
            },
        )
    )

    assert captured["project_directory"] == "api"
    assert captured["refresh"] == "always"
