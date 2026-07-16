from pathlib import Path

from create_python_app_core.loaders import merge_layers
from create_python_app_core.paths import ResolvedSource
from create_python_app_core.pyproject_merge import (
    dependency_name,
    merge_dependency_lists,
    merge_pyproject_text,
)


def _layer(tmp: Path, name: str, files: dict[str, str]) -> tuple[ResolvedSource, Path]:
    root = tmp / name
    tpl = root / "template"
    for rel, content in files.items():
        path = tpl / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    src = ResolvedSource(kind="file", url=f"file://{root}", local_path=root)
    return src, root


def test_dependency_name() -> None:
    assert dependency_name("fastapi>=0.115") == "fastapi"
    assert dependency_name("psycopg[binary]>=3.0") == "psycopg"
    assert dependency_name("Foo_Bar==1.0") == "foo-bar"


def test_merge_dependency_lists_later_wins() -> None:
    merged = merge_dependency_lists(
        ["fastapi>=0.100", "uvicorn>=0.30"],
        ["fastapi>=0.115", "httpx>=0.28"],
    )
    assert merged == ["fastapi>=0.115", "uvicorn>=0.30", "httpx>=0.28"]


def test_merge_pyproject_text_unions_deps() -> None:
    base = """
[project]
name = "base"
dependencies = ["fastapi>=0.100"]

[dependency-groups]
dev = ["pytest>=8"]
"""
    overlay = """
[project]
dependencies = ["fastapi>=0.115", "uvicorn>=0.32"]

[dependency-groups]
dev = ["ruff>=0.8"]

[tool.ruff]
line-length = 100
"""
    merged = merge_pyproject_text(base, overlay)
    assert "fastapi>=0.115" in merged
    assert "uvicorn>=0.32" in merged
    assert "pytest>=8" in merged
    assert "ruff>=0.8" in merged
    assert "line-length = 100" in merged


def test_merge_layers_merges_pyproject(tmp_path: Path) -> None:
    a = _layer(
        tmp_path,
        "a",
        {
            "pyproject.toml": (
                '[project]\nname = "app"\ndependencies = ["fastapi>=0.100"]\n'
            )
        },
    )
    b = _layer(
        tmp_path,
        "b",
        {
            "pyproject.toml": (
                '[project]\ndependencies = ["uvicorn>=0.32"]\n'
                '[dependency-groups]\ndev = ["ruff>=0.8"]\n'
            )
        },
    )
    dest = tmp_path / "out"
    merge_layers([a, b], dest)
    text = (dest / "pyproject.toml").read_text()
    assert 'name = "app"' in text
    assert "fastapi>=0.100" in text
    assert "uvicorn>=0.32" in text
    assert "ruff>=0.8" in text
