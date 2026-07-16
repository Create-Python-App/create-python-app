from pathlib import Path

import pytest
from create_python_app_core.config import CpaConfig
from create_python_app_core.errors import IncompatibleExtensionsError
from create_python_app_core.installer import (
    scaffold_project,
    validate_config_incompatible_extensions,
)
from create_python_app_core.paths import ResolvedSource


def _tpl(tmp: Path, name: str) -> str:
    root = tmp / name
    (root / "template").mkdir(parents=True)
    (root / "template" / "hello.txt").write_text("hi")
    (root / "cpa.config.json").write_text('{"name":"t"}')
    return f"file://{root}"


def _ext(tmp: Path, name: str, *, incompatible: list[str] | None = None) -> str:
    root = tmp / name
    (root / "template").mkdir(parents=True)
    (root / "template" / f"{name}.txt").write_text(name)
    payload = {"name": name}
    if incompatible:
        payload["incompatibleWith"] = incompatible
    import json

    (root / "cpa.config.json").write_text(json.dumps(payload))
    return f"file://{root}"


def test_scaffold_file_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    dest = tmp_path / "app"
    url = _tpl(tmp_path, "tpl")
    scaffold_project(str(dest), template=url, install=False)
    assert (dest / "hello.txt").read_text() == "hi"


def test_scaffold_forwards_refresh_to_download_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    dest = tmp_path / "app"
    url = _tpl(tmp_path, "tpl")
    refresh_values: list[str | None] = []

    def fake_download_repository(
        source: ResolvedSource,
        *,
        offline: bool = False,
        refresh: str | None = None,
        cache_root: Path | None = None,
    ) -> Path:
        refresh_values.append(refresh)
        assert offline is False
        assert cache_root is None
        assert source.local_path is not None
        return source.local_path

    monkeypatch.setattr(
        "create_python_app_core.installer.download_repository",
        fake_download_repository,
    )

    scaffold_project(str(dest), template=url, install=False, refresh="always")

    assert refresh_values == ["always"]


def test_validate_config_incompatible_extensions_raises() -> None:
    configs = [
        CpaConfig(name="template", raw={}),
        CpaConfig(name="saga", raw={"incompatibleWith": ["thunk"]}),
        CpaConfig(name="thunk", raw={"incompatibleWith": ["saga"]}),
    ]
    with pytest.raises(IncompatibleExtensionsError, match="saga"):
        validate_config_incompatible_extensions(configs)


def test_scaffold_rejects_config_incompatible_extensions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CPA_SKIP_GIT", "1")
    dest = tmp_path / "app"
    template = _tpl(tmp_path, "tpl")
    a = _ext(tmp_path, "saga", incompatible=["thunk"])
    b = _ext(tmp_path, "thunk", incompatible=["saga"])
    with pytest.raises(IncompatibleExtensionsError, match="saga"):
        scaffold_project(
            str(dest),
            template=template,
            addons=[a, b],
            install=False,
        )
    assert not dest.exists()
