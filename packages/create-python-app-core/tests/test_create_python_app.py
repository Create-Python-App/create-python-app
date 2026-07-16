from pathlib import Path

import pytest
from create_python_app_core import create_python_app


@pytest.mark.asyncio
async def test_create_python_app_file_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    root = tmp_path / "tpl"
    (root / "template").mkdir(parents=True)
    (root / "template" / "x.txt").write_text("ok")
    dest = tmp_path / "out"
    await create_python_app(
        str(dest),
        {"template": f"file://{root}", "install": False},
    )
    assert (dest / "x.txt").read_text() == "ok"
