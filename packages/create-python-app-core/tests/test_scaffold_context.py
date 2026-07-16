from pathlib import Path

import pytest
from create_python_app_core.config import CpaConfig, CpaCustomOption
from create_python_app_core.installer import build_scaffold_context, scaffold_project


def test_build_scaffold_context_merges_defaults_and_set() -> None:
    cfg = CpaConfig(
        custom_options=[
            CpaCustomOption(key="apiPrefix", default="/api/v1"),
            CpaCustomOption(key="enableCors", default="true"),
        ]
    )
    ctx = build_scaffold_context(
        "my-api",
        [cfg],
        {"set": {"enableCors": "false", "extra": "1"}},
    )
    assert ctx == {
        "projectName": "my-api",
        "apiPrefix": "/api/v1",
        "enableCors": "false",
        "extra": "1",
    }


def test_scaffold_renders_template_from_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    root = tmp_path / "tpl"
    (root / "template").mkdir(parents=True)
    (root / "template" / "hello.txt.template").write_text(
        "hi {{ projectName }} {{ tag }}\n"
    )
    dest = tmp_path / "app"
    scaffold_project(
        str(dest),
        template=f"file://{root}",
        install=False,
        options={"set": {"tag": "x"}},
    )
    assert (dest / "hello.txt").read_text() == "hi app x\n"
